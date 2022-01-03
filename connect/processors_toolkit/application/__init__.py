from __future__ import annotations

import pinject

from enum import Enum, unique
from abc import ABC
from logging import Logger
from typing import Any, Dict, Optional, Type

from connect.client import ConnectClient
from connect.eaas.extension import Extension


@unique
class BindType(Enum):
    TO_CLASS = 'to_class'
    TO_INSTANCE = 'to_instance'


class Dependencies:
    """
    Dependency declarations.

    to_class:
        Define a dependency binding the dependency key to a certain class.
            dependencies.to_class('request_builder', RequestBuilder)

    to_instance:
        Define a dependency binding the dependency key to a certain instance.
            dependencies.to_class('service_api_key', 'XXXXXXXXXXX')

    bind:
        Raw dependency binding.
            dependencies.bind('service_api_key', BindType.TO_INSTANCE, 'XXXXXXXXXXX')

    """

    def __init__(self, dependencies: Optional[dict] = None):
        self.binds = {} if dependencies is None else dependencies

    def bind(self, name: str, to: BindType, thing: Any) -> Dependencies:
        self.binds.update({name: {to.value: thing}})
        return self

    def to_class(self, name: str, thing: Any) -> Dependencies:
        return self.bind(name, BindType.TO_CLASS, thing)

    def to_instance(self, name: str, thing: Any) -> Dependencies:
        return self.bind(name, BindType.TO_INSTANCE, thing)


class Container:
    """
    Dependency Container based in the PInject project.
    """

    def __init__(self, dependencies: Dependencies):
        class __DISpec(pinject.BindingSpec):
            def __init__(self, dependencies: Dependencies):
                self.__dependencies = dependencies

            def configure(self, bind):
                for name, dependency in self.__dependencies.binds.items():
                    bind(name, **dependency)

        self.__container = pinject.new_object_graph(
            binding_specs=[__DISpec(dependencies)],
            # disable the auto-search for implicit bindings.
            modules=None,
        )

    def get(self, cls) -> Any:
        return self.__container.provide(cls)


class Application(Extension, ABC):
    """
    Main Application Class

    Defines the entrypoint of the service and creates the dependency
    container with all the declared dependencies.
    """

    def __init__(
            self,
            client: ConnectClient,
            logger: Logger,
            config: Dict[str, str],
            dependencies: Optional[Dependencies] = None,
    ):
        super().__init__(client, logger, config)

        dependencies = self.dependencies() if dependencies is None else dependencies
        dependencies.to_instance('config', config)
        dependencies.to_instance('client', client)
        dependencies.to_instance('logger', logger)
        for key, value in config.items():
            dependencies.to_instance(key, value)

        self.__container = Container(dependencies)

    @property
    def container(self) -> Container:
        return self.__container

    def dependencies(self) -> Dependencies:
        return Dependencies()

    def make(self, cls: Type) -> Any:
        """
        Makes the requested class by type.

        :param cls: The class type.
        :return: Object
        """
        return self.container.get(cls)
