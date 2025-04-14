import asyncio
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

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        self.state = {}
        planner_key = f"{self.planner_executor.agent.name}_input"
        planner_input = {planner_key: input_data}
        max_iterations = 10

        for iteration in range(max_iterations):
            print(f"\n=== Iteration {iteration + 1} ===")
            terminated = await self._run_one_full_pass(planner_input)
            if terminated:
                break

            # Prepare planner input for next iteration
            planner_input = {
                planner_key: {
                    ex.agent.name: self.state.get(ex, {})
                    for ex in self.state
                }
            }

        # Final step: run output executors if terminated
        final_outputs = {}
        for executor in self.graph.get_output_executors():
            input_key = f"{executor.agent.name}_input"
            inputs = {
                input_key: {
                    ex.agent.name: self.state.get(ex, {})
                    for ex in self.state
                }
            }
            _, result = await self._run_executor(executor, inputs)
            self.state[executor] = result
            final_outputs[executor.agent.name] = result

        return final_outputs

    async def _run_one_full_pass(self, planner_input: Dict[str, Any]) -> bool:
        execution_layers = self.graph.get_execution_layers(include_output_executors=False)

        for layer in execution_layers:
            # Step 1: Ask planner who to run
            _, planner_output = await self._run_executor(self.planner_executor, planner_input)
            self.state[self.planner_executor] = planner_output

            if planner_output.get("terminate", False):
                return True

            selected_names = planner_output.get("next_executors", [])
            selected_executors = [
                ex for ex in layer
                if ex.agent.name in selected_names and ex != self.planner_executor
            ]

            # Step 2: Run selected executors from this layer
            if selected_executors:
                tasks = []
                for ex in selected_executors:
                    inputs = self._collect_upstream_outputs(ex, planner_input)
                    tasks.append(self._run_executor(ex, inputs))
                results = await asyncio.gather(*tasks)
                for ex, output in results:
                    self.state[ex] = output

        return False
