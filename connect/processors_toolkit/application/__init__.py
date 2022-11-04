#
# This file is part of the Ingram Micro CloudBlue Connect Processors Toolkit.
#
# Copyright (c) 2022 Ingram Micro. All Rights Reserved.
#
from __future__ import annotations

from abc import ABC
from logging import LoggerAdapter
from typing import Dict, Optional, Union

from connect.client import AsyncConnectClient, ConnectClient
from connect.eaas.extension import Extension
from connect.processors_toolkit.dependency_injection.container import (  # noqa: F401
    Container,
    Dependencies,
    DependencyBuildingFailure,
)
from connect.processors_toolkit.requests import RequestBuilder


class Application(Extension, ABC):
    """
    Main Application Class

    Defines the entrypoint of the service and creates the dependency
    container with all the declared dependencies.
    """

    def __init__(
            self,
            client: Union[ConnectClient, AsyncConnectClient],
            logger: LoggerAdapter,
            config: Dict[str, str],
            dependencies: Optional[Dependencies] = None,
    ):
        super().__init__(client, logger, config)

        self.__dependencies = self.dependencies() if dependencies is None else dependencies
        self.__dependencies.to_instance('config', config)
        self.__dependencies.to_instance('client', client)
        self.__dependencies.to_instance('logger', logger)
        for key, value in config.items():
            self.__dependencies.to_instance(key.lower(), value.strip())

        self.__container = Container.deferred()

    @property
    def container(self) -> Container:
        """
        Container Accessor. If the container is deferred this method
        will resolve it injecting the dependencies.

        :return: Container
        """
        if callable(self.__container):
            # if the container is callable, inject the dependencies
            # to the callable and resolve it, the
            self.__container = self.__container(self.__dependencies)

        return self.__container

    def dependencies(self) -> Dependencies:
        return Dependencies()

    def with_request(self, request: dict):
        """
        Attach the given request to the dependency spec and set
        the container as a deferred container, so it can resolve
        new dependencies using the newly attached request.

        :param request: dict The request to attach to the dependencies.
        :return: Application The application with the attached request.
        """
        self.__dependencies.to_instance('request', RequestBuilder(request))
        self.__container = Container.deferred()
        return self
