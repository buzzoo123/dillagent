import asyncio
from typing import Dict, Set, Any
from ...agents.agents import BaseAgent
from ..graphs.BaseAgentGraphExecutor import BaseAgentGraphExecutor
from ..graphs.StarterAgentGraph import StarterAgentGraph

class StarterAgentGraphExecutor(BaseAgentGraphExecutor):
    def __init__(self, graph: StarterAgentGraph):
        super().__init__(graph)
        self.graph = graph  # Cast to correct type for IDE support
        
        # Additional validation
        if self.graph.input_agent is None:
            raise ValueError("Graph must have input_agent defined")
        if self.graph.output_agent is None:
            raise ValueError("Graph must have output_agent defined")

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the graph from input_agent to output_agent using a wave-based approach.
        """
        agent_outputs = {}
        completed = set()
        
        # Start with input agent
        try:
            agent_outputs[self.graph.input_agent] = await self.graph.input_agent.run(inputs=input_data)
            completed.add(self.graph.input_agent)
        except Exception as e:
            raise RuntimeError(f"Input agent failed with error: {str(e)}") from e
            
        ready = self._get_ready_agents(completed)
        wave_number = 0

        while ready:
            wave_number += 1
            print(f"Starting wave {wave_number} with {len(ready)} agents")
            wave_start = asyncio.get_event_loop().time()
            
            tasks = []
            for agent in ready:
                inputs = {
                    dep.name: agent_outputs[dep]
                    for dep in self.graph.reverse_edges[agent]
                }
                tasks.append(self._run_and_store(agent, inputs, agent_outputs, completed))

            # Run all ready agents concurrently
            await asyncio.gather(*tasks)
            
            wave_duration = asyncio.get_event_loop().time() - wave_start
            print(f"Completed wave {wave_number} in {wave_duration:.2f}s")
            
            ready = self._get_ready_agents(completed)

        # Ensure output agent has completed
        if self.graph.output_agent not in completed:
            raise RuntimeError("Graph execution completed but output agent was never executed")
            
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