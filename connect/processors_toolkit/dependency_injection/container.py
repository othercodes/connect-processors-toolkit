#
# This file is part of the Ingram Micro CloudBlue Connect Processors Toolkit.
#
# Copyright (c) 2022 Ingram Micro. All Rights Reserved.
#
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Type, Union

from pinject.bindings import BindingSpec
from pinject.errors import NothingInjectableForArgError, WrongArgTypeError
from pinject.object_graph import new_object_graph, ObjectGraph

from connect.processors_toolkit.dependency_injection.contracts import DIContainer
from connect.processors_toolkit.dependency_injection.exceptions import DependencyBuildingFailure, InvalidClassType


class ServiceProvider(BindingSpec):
    TO_CLASS = 'to_class'
    TO_INSTANCE = 'to_instance'

    def __init__(self, binds: Optional[Dict[str, Dict[str, Any]]] = None):
        self.__binds: Dict[str, Dict[str, Any]] = {} if binds is None else binds

    def configure(self, bind):
        self.register()

        for name, dependency in self.__binds.items():
            bind(name, **dependency)

    def register(self):
        """
        Place to execute the explicit binding of your service.

        def register(self):
            self.bind_instance('foo', 'foo')
            self.bind_class('cache', RedisCache)

        The available binding methods are:

        self.bind_class()
            Define a dependency binding between a key to a class.
            > dependencies.to_class('request_builder', RequestBuilder)

        self.bind_instance()
            Define a dependency binding the dependency key to a certain instance.
            > dependencies.to_class('service_api_key', 'some_api_key')

        :return: None
        """

    def bind_class(self, keyword: str, concrete: Any) -> ServiceProvider:
        self.__binds.update({keyword: {self.TO_CLASS: concrete}})
        return self

    def bind_instance(self, keyword: str, concrete: Any) -> ServiceProvider:
        self.__binds.update({keyword: {self.TO_INSTANCE: concrete}})
        return self


class Container(DIContainer):
    def __init__(self, providers: List[Type[ServiceProvider]]):
        def __make_container() -> ObjectGraph:
            return new_object_graph(
                binding_specs=[provider() for provider in providers],
                # disable the auto-search for implicit bindings.
                modules=None,
            )

        self.__container: Union[ObjectGraph, Callable[[], ObjectGraph]] = __make_container

    def get(self, cls: Type) -> Any:
        try:
            if callable(self.__container):
                self.__container = self.__container()
            return self.__container.provide(cls)

        except NothingInjectableForArgError as e:
            raise DependencyBuildingFailure(str(e))

        except WrongArgTypeError as e:
            raise InvalidClassType(str(e))
