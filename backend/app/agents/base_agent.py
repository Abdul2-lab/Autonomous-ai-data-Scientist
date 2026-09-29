"""
Base class for all agents. Each agent takes real data (a DataFrame and/or
prior stage outputs) and returns a structured, JSON-serializable dict.
No agent invents numbers -- everything here is computed with pandas/numpy/sklearn.
"""
from abc import ABC, abstractmethod


class BaseAgent(ABC):
    name: str = "base_agent"

    @abstractmethod
    def run(self, *args, **kwargs) -> dict:
        raise NotImplementedError
