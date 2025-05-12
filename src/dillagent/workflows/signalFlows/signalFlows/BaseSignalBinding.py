from typing import List, Callable, Awaitable
from dataclasses import dataclass
from .BaseSignal import BaseSignal
from ....agents.executors.BaseAgentExecutor import BaseAgentExecutor

@dataclass
class BaseSignalBinding:
    agent_name: str
    executor: BaseAgentExecutor
    subscribed_signal_types: List[str]

    def should_trigger(self, signal: BaseSignal) -> bool:
        return signal.type in self.subscribed_signal_types

    async def handle_signal(self, signal: BaseSignal) -> List[BaseSignal]:
        result = await self.executor.run(signal.payload)

        return [
            BaseSignal.spawn(
                type=f"{self.agent_name}.output",
                payload=result,
                source=self.agent_name
            )
        ]
