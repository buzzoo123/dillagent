from abc import abstractmethod
from typing import Dict, Any, Set
from ....agents.executors.BaseAgentExecutor import BaseAgentExecutor
from ..graphs.BaseAgentGraph import BaseAgentGraph
from ...BaseWorkflowExecutor import BaseWorkflowExecutor
import asyncio

class BaseAgentGraphExecutor(BaseWorkflowExecutor):
    def __init__(self, graph: BaseAgentGraph):
        self.graph = graph
        self.graph.validate_graph()
        self.execution_layers = graph.get_execution_layers()
        self.state: Dict[BaseAgentExecutor, Dict[str, Any]] = {}

    @abstractmethod
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Subclass defines how the graph is executed over time.
        Typically calls `run_iteration(...)` one or more times.
        """
        pass

    async def run_iteration(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        executed: Set[BaseAgentExecutor] = set()

        for layer in self.execution_layers:
            tasks = []
            for executor in layer:
                upstream_inputs = self._collect_upstream_outputs(executor, input_data)
                tasks.append(self._run_executor(executor, upstream_inputs))

            results = await asyncio.gather(*tasks)

            for executor, output in results:
                self.state[executor] = output
                executed.add(executor)

        return self._collect_final_outputs()

    async def _run_executor(self, executor: BaseAgentExecutor, inputs: Dict[str, Any]):
        output = await executor.run(inputs)
        
        return executor, output

    def _collect_upstream_outputs(self, executor: BaseAgentExecutor, input_data: Dict[str, Any]) -> Dict[str, Any]:
        upstream = self.graph.get_upstream_executors(executor)
        if not upstream:
            return input_data

        merged = {}
        for u in upstream:
            merged[f"{u.agent.name}_input"] = self.state.get(u, {})
        return merged

    def _collect_final_outputs(self) -> Dict[str, Any]:
        output = {}
        for executor in self.graph.get_output_executors():
            output[executor.agent.name] = self.state.get(executor, {})
        return output
