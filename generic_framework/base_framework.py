from abc import ABC, abstractmethod

class FrameworkLogic(ABC):
    @abstractmethod
    async def run_task(self,user_query: str):
        pass