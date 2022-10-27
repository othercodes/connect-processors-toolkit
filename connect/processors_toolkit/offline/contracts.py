from abc import ABC, abstractmethod


class OfflineChecker(ABC):
    @abstractmethod
    def is_offline_enabled(self, request: dict) -> bool:
        """
        Evaluates if the given request is in offline mode or not.

        :param request: Union[dict, RequestBuilder] The Connect Request object.
        :return: bool True if the request is in offline model, False otherwise.
        """
