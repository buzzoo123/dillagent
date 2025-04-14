import asyncio
import json
from typing import Dict, Any
from ..graphs.BaseAgentGraph import BaseAgentGraph
from .BaseAgentGraphExecutor import BaseAgentGraphExecutor
from ....agents.executors.BaseAgentExecutor import BaseAgentExecutor

class PlannerAgentGraphExecutor(BaseAgentGraphExecutor):
    def __init__(self, graph: BaseAgentGraph, planner_executor: BaseAgentExecutor):
        self.graph = graph
        self.planner_executor = planner_executor
        self.state: Dict[BaseAgentExecutor, Dict[str, Any]] = {}

        if planner_executor not in graph.get_all_executors():
            raise ValueError("Planner must be part of the graph.")
        
    def _prepare_planner_input_for_next_iteration(self, state, original_query):
        # Flatten executor state to agent-name: output mapping
        flattened_state = {
            executor.agent.name: output
            for executor, output in state.items()
        }

        # Merge into single JSON-like dict
        planner_input_dict = {
            "original_query": original_query,
            **flattened_state
        }

        # Return as properly formatted input
        return {
            "PlannerAgent_input": json.dumps(planner_input_dict, indent=2)
        }

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        self.state = {}
        self.original_query = input_data.get("PlannerAgent_input", "")
        planner_key = f"{self.planner_executor.agent.name}_input"
        planner_input = {planner_key: self.original_query}  # FIXED LINE}
        max_iterations = 3

        for iteration in range(max_iterations):
            print(f"Overall State: {self.state}")
            print(f"\n=== Iteration {iteration + 1} ===")
            terminated = await self._run_one_full_pass(planner_input)
            if terminated:
                break

            # Prepare planner input for next iteration
            planner_input = self._prepare_planner_input_for_next_iteration(
                self.state, 
                self.original_query
            )

        # Final step: run output executors if terminated
        print("successfully terminated")
        final_outputs = {}
        for executor in self.graph.get_output_executors():
            input_key = f"{executor.agent.name}_input"
            inputs = self.state[self.planner_executor]
            print(f'final inputs {inputs}')
            _, result = await self._run_executor(executor, inputs)
            self.state[executor] = result
            final_outputs[executor.agent.name] = result

        return final_outputs

    async def _run_one_full_pass(self, planner_input: Dict[str, Any]) -> bool:
        execution_layers = self.graph.get_execution_layers(include_output_executors=True)
        print(f"Execution Layers: {execution_layers}")

        for layer in execution_layers:
            if self.planner_executor in layer:
                continue
            # Step 1: Ask planner who to run
            print(f"Planner Input: {planner_input}")
            _, planner_output = await self._run_executor(self.planner_executor, planner_input)
            print(f"Planner Output: {planner_output}")
            self.state[self.planner_executor] = planner_output

            if planner_output.get("terminate", False):
                return True

            selected_names = planner_output.get("next_executors", [])
            print("Executors in Layer before selection:")
            [print(ex.agent.name) for ex in layer]
            selected_executors = [
                ex for ex in layer
                if ex.agent.name in selected_names and ex != self.planner_executor
            ]
            print(f"selected_executors: {selected_executors}")
            if selected_executors:
                tasks = []
                for ex in selected_executors:
                    # Get the specific input for this agent from the planner's output
                    agent_input_key = f"{ex.agent.name}_input"
                    agent_input = planner_output.get(agent_input_key, "")
                    
                    # Create proper input format for the agent

                    print(f"inputs to {ex.agent.name}")

                    tasks.append(self._run_executor(ex, {agent_input_key: agent_input}))
                
                results = await asyncio.gather(*tasks)
                print(f"results from running executors: {results}")
                for ex, output in results:
                    self.state[ex] = output

        return False