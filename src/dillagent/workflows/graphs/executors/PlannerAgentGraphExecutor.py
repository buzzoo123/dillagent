import asyncio
import json
from typing import Dict, Any, List
from ..graphs.BaseAgentGraph import BaseAgentGraph
from .BaseAgentGraphExecutor import BaseAgentGraphExecutor
from ....agents.executors.BaseAgentExecutor import BaseAgentExecutor

class PlannerAgentGraphExecutor(BaseAgentGraphExecutor):
    def __init__(self, graph: BaseAgentGraph, planner_executor: BaseAgentExecutor, logging_enabled: bool = False):
        self.graph = graph
        self.planner_executor = planner_executor
        self.logging_enabled = logging_enabled
        self.state: Dict[BaseAgentExecutor, Dict[str, Any]] = {}
        
    def _prepare_planner_input_for_next_iteration(self, state, layer: List[BaseAgentExecutor], original_query):
        # Flatten executor state to agent-name: output mapping
        flattened_state = {
            "exectuor_states_from_last_iteration": {
            executor.agent.name: output
            for executor, output in state.items()
            }
        }

        available_agents = [f'{ex.agent.name}: {ex.agent.describe()}' for ex in layer]

        # Merge into single JSON-like dict
        planner_input_dict = {
            "original_query": original_query,
            "available_agents": available_agents,
            **flattened_state
        }

        output = {"PlannerAgent_input": json.dumps(planner_input_dict, indent=2)}

        # Return as properly formatted input
        return output

    async def run(self, input_data: Dict[str, Any], max_iterations=10) -> Dict[str, Any]:
        self.state = {}
        self.original_query = input_data.get("PlannerAgent_input", "")
        planner_key = f"{self.planner_executor.agent.name}_input"
        planner_input = {planner_key: self.original_query}
        iteration = 0

        while True:
            if max_iterations is not None and iteration >= max_iterations:
                break
            
            terminated = await self._run_one_full_pass(planner_input)
            if terminated:
                break

            # Prepare planner input for next iteration

    async def _run_one_full_pass(self, planner_input: Dict[str, Any]) -> bool:
        execution_layers = self.graph.get_execution_layers(include_output_executors=True)
        for layer in execution_layers:
            # Prepare Input to planner
            planner_input = self._prepare_planner_input_for_next_iteration(
                    self.state, 
                    layer,
                    self.original_query
            )
            if self.logging_enabled: print(planner_input)
            # Ask planner who to run
            _, planner_output = await self._run_executor(self.planner_executor, planner_input)
            # self.state[self.planner_executor] = planner_output



            if self.logging_enabled: print(planner_output)

            if planner_output.get("terminate", False) and len(planner_output.get("next_executors", [])) == 0:
                return True

            selected_names = planner_output.get("next_executors", [])
            if self.logging_enabled: print(selected_names) 
            selected_executors = [
                ex for ex in layer
                if ex.agent.name in selected_names and ex != self.planner_executor
            ]
            if selected_executors:
                tasks = []
                for ex in selected_executors:
                    # Get the specific input for this agent from the planner's output
                    agent_input_key = f"{ex.agent.name}_input"
                    agent_input = planner_output.get(agent_input_key, "")
                    
                    tasks.append(self._run_executor(ex, {agent_input_key: agent_input}))
                
                results = await asyncio.gather(*tasks)
                for ex, output in results:
                    self.state[ex] = output
            
            if planner_output.get("terminate", False):
                return True

        return False