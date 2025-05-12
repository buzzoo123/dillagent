import asyncio
from typing import List
from ..signalFlows.BaseSignalBinding import BaseSignalBinding
from ..signalFlows.BaseSignal import BaseSignal

class BaseSignalFlowExecutor:
    def __init__(self):
        self.agents: List[BaseSignalBinding] = []
        self.queue: asyncio.Queue[BaseSignal] = asyncio.Queue()

    def register(self, signal_flow: BaseSignalBinding):
        self.agents.append(signal_flow)

    async def publish(self, signal: BaseSignal):
        await self.queue.put(signal)

    async def run(self, initial_signals: List[BaseSignal]):
        for signal in initial_signals:
            await self.publish(signal)

        while not self.queue.empty():
            signal = await self.queue.get()

            for flow in self.agents:
                if flow.should_trigger(signal):
                    new_signals = await flow.handle_signal(signal)
                    for s in new_signals:
                        await self.publish(s)
