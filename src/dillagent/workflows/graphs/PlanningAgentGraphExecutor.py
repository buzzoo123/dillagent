import asyncio
from typing import Dict, Set, Any
from ...agents.agents import BaseAgent
from ..graphs.BaseAgentGraphExecutor import BaseAgentGraphExecutor
from ..graphs.StarterAgentGraph import StarterAgentGraph
from ...dependencies.parsers.intermediate.BaseIntermediateParser import BaseIntermediateParser

class PlanningAgentGraphExecutor(BaseAgentGraphExecutor):
    def __init__(self, graph: StarterAgentGraph, intermediate_parser: BaseIntermediateParser):
        super().__init__(graph)
        self.graph = graph
        self.im_parser = intermediate_parser
        
        # The planning agent controls execution flow
        self.planning_agent = None
        
        # Additional validation
        if self.graph.input_agent is None:
            raise ValueError("Graph must have input_agent defined")
        if self.graph.output_agent is None:
            raise ValueError("Graph must have output_agent defined")
        
        # Dictionary to keep track of all agents by name
        self.agent_map = {}
    
    def set_planning_agent(self, agent: BaseAgent):
        """Set the planning agent that will control execution flow."""
        self.planning_agent = agent
        
        # Ensure planning agent is in the graph
        found = False
        for agents in [self.graph.edges.keys(), *self.graph.edges.values()]:
            if agent in agents:
                found = True
                break
                
        if not found:
            # Add planning agent to the graph if not already present
            self.graph.add_edge(self.graph.input_agent, agent)
            self.graph.add_edge(agent, self.graph.output_agent)

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the graph with the planning agent controlling the flow.
        """
        if self.planning_agent is None:
            raise ValueError("Planning agent must be set before execution")
        
        # Build a map of agent names to agent objects for easy lookup
        self._build_agent_map()
        
        agent_outputs = {}
        completed_agents = set()
        iteration = 0
        
        # Start with input agent (which is the planning agent in your setup)
        input_agent = self.graph.input_agent
        try:
            output_text = await input_agent.run(inputs=input_data)
            parsed_output = self._parse_agent_output(output_text)
            agent_outputs[input_agent] = parsed_output
            completed_agents.add(input_agent)
            
            print(f"Input agent completed: {input_agent.name if hasattr(input_agent, 'name') else str(input_agent)}")
        except Exception as e:
            raise RuntimeError(f"Input agent failed with error: {str(e)}") from e
        
        # Main planning loop - simpler dependency tracking
        plan = parsed_output  # Initial plan from input agent (planning agent)
        
        while iteration < 10:  # Prevent infinite loops
            iteration += 1
            print(f"Iteration {iteration}")
            print(f"Agent Outputs {agent_outputs}")
            
            # Check for termination
            if plan.get("terminate", False):
                print("Planning agent has decided to terminate the workflow")
                break
                
            # Get the next agents to run from the plan
            next_agents = []
            for agent_name in plan.get("next_agents", []):
                # Find agent by name
                if agent_name in self.agent_map:
                    next_agents.append(self.agent_map[agent_name])
                else:
                    print(f"Warning: Agent '{agent_name}' from plan not found in graph")
            
            if not next_agents:
                print("No agents to run in this iteration")
                
                # If the planning agent is already completed, we can ask it again
                if self.planning_agent in completed_agents:
                    planning_inputs = {
                        "user_input": input_data,
                        "previous_outputs": {k.name if hasattr(k, "name") else str(k): v for k, v in agent_outputs.items()},
                        "iteration": iteration
                    }
                    
                    plan_text = await self.planning_agent.run(inputs=planning_inputs)
                    plan = self._parse_agent_output(plan_text)
                    agent_outputs[self.planning_agent] = plan
                    
                    # Continue to next iteration with new plan
                    continue
                else:
                    print("Planning agent not completed and no valid agents specified")
                    break
                
            # Run the selected agents in parallel
            tasks = []
            for agent in next_agents:
                # Prepare inputs - include outputs from all completed agents
                inputs = {
                    agent_name: agent_outputs[agent_obj]
                    for agent_name, agent_obj in self.agent_map.items()
                    if agent_obj in completed_agents
                }
                
                # Add planning context for this specific agent
                agent_name = agent.name if hasattr(agent, "name") else str(agent)
                inputs["planning_context"] = plan.get("agent_inputs", {}).get(agent_name, {})
                inputs["user_query"] = input_data.get("user_query", "")
                
                # Add task to run this agent
                tasks.append(self._run_agent(agent, inputs, agent_outputs, completed_agents))
                
            # Run agents concurrently
            if tasks:
                await asyncio.gather(*tasks)
            
            # Ask planning agent for next steps
            if self.planning_agent in completed_agents:
                planning_inputs = {
                    "user_input": input_data,
                    "previous_outputs": {k.name if hasattr(k, "name") else str(k): v for k, v in agent_outputs.items()},
                    "iteration": iteration
                }
                
                plan_text = await self.planning_agent.run(inputs=planning_inputs)
                plan = self._parse_agent_output(plan_text)
                agent_outputs[self.planning_agent] = plan
            else:
                print("Warning: Planning agent not in completed agents list")
                break
        
        # If output agent hasn't run yet, run it with all available outputs
        if self.graph.output_agent not in completed_agents:
            output_agent = self.graph.output_agent
            print(f"Running output agent: {output_agent.name if hasattr(output_agent, 'name') else str(output_agent)}")
            
            # Prepare inputs - include outputs from all completed agents
            inputs = {
                agent_name: agent_outputs[agent_obj]
                for agent_name, agent_obj in self.agent_map.items()
                if agent_obj in completed_agents
            }
            
            # Also include the final plan and user query
            inputs["final_plan"] = plan
            inputs["user_query"] = input_data.get("user_query", "")
            
            output_text = await output_agent.run(inputs=inputs)
            parsed_output = self._parse_agent_output(output_text)
            agent_outputs[output_agent] = parsed_output
            
        return agent_outputs.get(self.graph.output_agent, {})

    async def _run_agent(self, agent: BaseAgent, inputs: Dict[str, Any], 
                        agent_outputs: Dict, completed_agents: Set) -> None:
        """Run an agent with given inputs and store its output."""
        agent_name = agent.name if hasattr(agent, "name") else str(agent)
        print(f"Running agent: {agent_name}")
        
        try:
            output_text = await agent.run(inputs=inputs)
            parsed_output = self._parse_agent_output(output_text)
            agent_outputs[agent] = parsed_output
            completed_agents.add(agent)
            print(f"Agent completed: {agent_name}")
            
        except Exception as e:
            print(f"Error running agent {agent_name}: {str(e)}")
            # Don't throw error, just log it and continue
            agent_outputs[agent] = {"error": str(e)}
    
    def _parse_agent_output(self, output_text):
        """Parse agent output using the intermediate parser."""
        if isinstance(output_text, str):
            try:
                return self.im_parser.parse_values(output_text)
            except Exception as e:
                print(f"Warning: Failed to parse agent output: {str(e)}")
                return {"raw_output": output_text}
        else:
            # If it's already a dictionary, use it directly
            return output_text
    
    def _build_agent_map(self):
        """Build a map of agent names to agent objects for easy lookup."""
        # Collect all agents in the graph
        all_agents = set(self.graph.edges.keys())
        for downstreams in self.graph.edges.values():
            all_agents.update(downstreams)
            
        # Map agent names to agent objects
        self.agent_map = {}
        for agent in all_agents:
            name = agent.name
            self.agent_map[name] = agent
            
        print(f"Agent map built: {list(self.agent_map.keys())} Full map: {self.agent_map}")