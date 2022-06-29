from __future__ import annotations

import pinject
from pinject.errors import NothingInjectableForArgError

from enum import Enum, unique
from typing import Any, Callable, Optional


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


class DependencyBuildingFailure(Exception):
    pass


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

    @staticmethod
    def deferred() -> Callable[[Dependencies], Container]:
        def __make_container(dependencies: Dependencies) -> Container:
            return Container(dependencies)

        return __make_container

    def get(self, cls) -> Any:
        try:
            return self.__container.provide(cls)
        except NothingInjectableForArgError as e:
            raise DependencyBuildingFailure(str(e))
