from abc import ABC, abstractmethod
from collections import defaultdict
from typing import List, Set
from ....agents.executors.BaseAgentExecutor import BaseAgentExecutor

class BaseAgentGraph(ABC):
    def __init__(self):
        self.edges = defaultdict(list)           # executor -> downstream executors
        self.reverse_edges = defaultdict(list)   # executor -> upstream executors
        self.executors: Set[BaseAgentExecutor] = set()
        self._explicit_output_executors: Set[BaseAgentExecutor] = set()

    def add_executor(self, executor: BaseAgentExecutor):
        self.executors.add(executor)

    def add_edge(self, from_executor: BaseAgentExecutor, to_executor: BaseAgentExecutor):
        self.edges[from_executor].append(to_executor)
        self.reverse_edges[to_executor].append(from_executor)
        self.executors.update({from_executor, to_executor})

    def remove_edge(self, from_executor: BaseAgentExecutor, to_executor: BaseAgentExecutor):
        if to_executor in self.edges[from_executor]:
            self.edges[from_executor].remove(to_executor)
        if from_executor in self.reverse_edges[to_executor]:
            self.reverse_edges[to_executor].remove(from_executor)

    def get_input_executors(self) -> List[BaseAgentExecutor]:
        return [ex for ex in self.executors if not self.reverse_edges[ex]]

    def register_output_executor(self, executor: BaseAgentExecutor):
        self._explicit_output_executors.add(executor)

    def get_output_executors(self) -> List[BaseAgentExecutor]:
        if self._explicit_output_executors:
            return list(self._explicit_output_executors)
        raise ValueError("No output executors registered.")

    def get_all_executors(self) -> List[BaseAgentExecutor]:
        return list(self.executors)

    def get_downstream_executors(self, executor: BaseAgentExecutor) -> List[BaseAgentExecutor]:
        return self.edges.get(executor, [])

    def get_upstream_executors(self, executor: BaseAgentExecutor) -> List[BaseAgentExecutor]:
        return self.reverse_edges.get(executor, [])

    def validate_graph(self):
        try:
            self.get_execution_layers()
        except ValueError as e:
            raise ValueError(f"Graph validation failed: {e}")

        for executor in self.executors:
            if not self.edges[executor] and not self.reverse_edges[executor]:
                raise ValueError(f"Graph validation failed: Executor {executor} is isolated (no edges).")

    def get_execution_layers(self, include_output_executors: bool = True) -> List[Set[BaseAgentExecutor]]:
        # Kahn’s algorithm for topological sorting in layers
        in_degree = {ex: 0 for ex in self.executors}
        for downstreams in self.edges.values():
            for downstream in downstreams:
                in_degree[downstream] += 1

        ready = [ex for ex, deg in in_degree.items() if deg == 0]
        layers = []

        while ready:
            current_layer = set(ready)
            layers.append(current_layer)
            next_ready = []

            for executor in current_layer:
                for downstream in self.edges.get(executor, []):
                    in_degree[downstream] -= 1
                    if in_degree[downstream] == 0:
                        next_ready.append(downstream)

            ready = next_ready

        if any(deg > 0 for deg in in_degree.values()):
            raise ValueError("Cycle detected in graph. Cannot perform topological sort.")

        if not include_output_executors:
            output_executors = set(self.get_output_executors())
            layers[-1] = layers[-1] - output_executors
            if not layers[-1]:
                layers.pop()

        return layers
