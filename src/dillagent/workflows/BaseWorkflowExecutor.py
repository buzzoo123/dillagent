from abc import abstractmethod

class BaseWorkflowExecutor:
    def __init__(self):
        pass
    
    @abstractmethod
    def run(self):
        pass