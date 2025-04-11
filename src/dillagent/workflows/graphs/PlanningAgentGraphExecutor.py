import asyncio
from typing import Dict, Set, Any, Optional, List
from ...agents.agents import BaseAgent
from ..graphs.BaseAgentGraphExecutor import BaseAgentGraphExecutor
from ..graphs.StarterAgentGraph import StarterAgentGraph

class PlanningAgentGraphExecutor(BaseAgentGraphExecutor):
    def __init__(self, graph: StarterAgentGraph):
        super().__init__(graph)
        self.graph = graph
        
        # The planning agent controls execution flow
        self.planning_agent = None
        
        # Additional validation
        if self.graph.input_agent is None:
            raise ValueError("Graph must have input_agent defined")
        if self.graph.output_agent is None:
            raise ValueError("Graph must have output_agent defined")
    
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
        
        agent_outputs = {}
        completed = set()
        execution_state = {
            "completed_agents": [],
            "available_agents": [],
            "pending_agents": [],
            "current_plan": [],
            "iteration": 0
        }
        
        # Start with input agent
        try:
            output = await self.graph.input_agent.run(inputs=input_data)
            agent_outputs[self.graph.input_agent] = output
            completed.add(self.graph.input_agent)
            execution_state["completed_agents"].append(self.graph.input_agent.name 
                                                      if hasattr(self.graph.input_agent, "name") 
                                                      else str(self.graph.input_agent))
        except Exception as e:
            raise RuntimeError(f"Input agent failed with error: {str(e)}") from e
        
        # Initialize available agents
        available_agents = self._get_ready_agents(completed)
        execution_state["available_agents"] = [a.name if hasattr(a, "name") else str(a) for a in available_agents]
        
        # Calculate all potential agents
        all_agents = set(self.graph.edges.keys())
        for downstreams in self.graph.edges.values():
            all_agents.update(downstreams)
        all_agents.discard(self.graph.input_agent)
        all_agents.discard(self.graph.output_agent)
        all_agents.discard(self.planning_agent)
        
        # Initialize pending agents
        pending_agents = all_agents - available_agents - completed
        execution_state["pending_agents"] = [a.name if hasattr(a, "name") else str(a) for a in pending_agents]
        
        # Main planning loop
        while execution_state["iteration"] < 10:
            execution_state["iteration"] += 1
            
            # Ask planning agent for next steps
            planning_inputs = {
                "execution_state": execution_state,
                "previous_outputs": {k.name if hasattr(k, "name") else str(k): v for k, v in agent_outputs.items()},
                "user_input": input_data
            }
            
            plan = await self.planning_agent.run(inputs=planning_inputs)
            agent_outputs[self.planning_agent] = plan
            
            if not isinstance(plan, dict):
                raise RuntimeError("Planning agent must return a dictionary")
                
            # Check for termination
            if plan.get("terminate", False):
                break
                
            # Get the next agents to run from the plan
            next_agents = []
            for agent_name in plan.get("next_agents", []):
                # Find agent by name
                target_agent = None
                for agent in all_agents:
                    if hasattr(agent, "name") and agent.name == agent_name:
                        target_agent = agent
                        break
                
                if target_agent is None:
                    print(f"Warning: Agent '{agent_name}' from plan not found in graph")
                    continue
                    
                # Check if agent is available (all dependencies satisfied)
                if target_agent in available_agents:
                    next_agents.append(target_agent)
                else:
                    print(f"Warning: Agent '{agent_name}' is not available yet (dependencies not satisfied)")
            
            if not next_agents:
                print("No valid agents to run in this iteration")
                
                # If no agents left to run, check if we should terminate
                if not available_agents and not pending_agents:
                    print("No more agents available to run, terminating execution")
                    break
                continue
                
            # Run the selected agents in parallel
            tasks = []
            for agent in next_agents:
                inputs = {
                    dep.name: agent_outputs[dep]
                    for dep in self.graph.reverse_edges[agent]
                    if dep in agent_outputs
                }
                # Add planning context
                inputs["planning_context"] = plan.get("agent_inputs", {}).get(agent.name if hasattr(agent, "name") else str(agent), {})
                
                tasks.append(self._run_and_store(agent, inputs, agent_outputs, completed))
                
            # Run agents concurrently
            await asyncio.gather(*tasks)
            
            # Update execution state
            available_agents = self._get_ready_agents(completed)
            pending_agents = all_agents - available_agents - completed
            
            execution_state["available_agents"] = [a.name if hasattr(a, "name") else str(a) for a in available_agents]
            execution_state["pending_agents"] = [a.name if hasattr(a, "name") else str(a) for a in pending_agents]
            execution_state["completed_agents"] = [a.name if hasattr(a, "name") else str(a) for a in completed]
            execution_state["current_plan"] = plan
        
        # Run output agent if not already completed
        if self.graph.output_agent not in completed:
            inputs = {
                dep.name: agent_outputs[dep]
                for dep in self.graph.reverse_edges[self.graph.output_agent]
                if dep in agent_outputs
            }
            # Add final plan
            inputs["final_plan"] = plan
            
            output = await self.graph.output_agent.run(inputs=inputs)
            agent_outputs[self.graph.output_agent] = output
            
        return agent_outputs.get(self.graph.output_agent, {})

    async def _run_and_store(self, agent: BaseAgent, inputs: Dict[str, Any], 
                            agent_outputs: Dict, completed: Set) -> None:
        """Run an agent with given inputs and store its output."""
        try:
            output = await agent.run(inputs=inputs)
            agent_outputs[agent] = output
            completed.add(agent)
        except Exception as e:
            # You may want to customize error handling behavior
            raise RuntimeError(f"Agent {agent.name if hasattr(agent, 'name') else agent} failed: {str(e)}") from e

    def _get_ready_agents(self, completed: Set) -> Set:
        """Get all agents that are ready to run (all dependencies completed)."""
        ready = set()
        for agent, deps in self.graph.reverse_edges.items():
            if agent not in completed and all(dep in completed for dep in deps):
                ready.add(agent)
        return ready