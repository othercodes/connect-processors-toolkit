from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Type


class DIContainer(ABC):
    @abstractmethod
    def get(self, cls: Type) -> Any:
        """
        Instantiate the given cls injecting the required dependencies.

        :param cls: Type The class name to instantiate.
        :return: Any A valid instance of the given class type.
        """
