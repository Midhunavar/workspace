"""
Base review agent.

Define BaseAgent as the abstract base for every review agent. It standardises the agent name, a
logger, a log() helper, and the abstract analyze(files_data) interface that each agent implements.
See the problem description for the contract.
"""
import logging
from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """Base class for all code-review agents."""

    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"agent.{name}")

    def log(self, message: str, level: str = "info") -> None:
        log_method = getattr(self.logger, level, self.logger.info)
        log_method(message)

    @abstractmethod
    def analyze(self, files_data: list) -> list:
        """Analyze files and return per-file results."""
        raise NotImplementedError
