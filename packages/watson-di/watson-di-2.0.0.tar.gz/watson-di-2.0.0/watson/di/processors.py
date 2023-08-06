# -*- coding: utf-8 -*-
import abc
from types import FunctionType
from watson.common import imports
from watson.common.contextmanagers import ignored
from watson import di
from watson.di.types import FUNCTION_TYPE, CLASS_TYPE


class Base(di.ContainerAware, metaclass=abc.ABCMeta):

    """The base processor that all other processors should extend.

    When a processor is called from the container the following parameters are
    sent through with the event.

        - definition: The dict definition of the dependency
        - dependency: The name of the dependency

    Depending on the event, a different target will also be sent with the event.

        - watson.di.container.PRE_EVENT: The dict definition of the dependency
        - watson.di.container.POST_EVENT: The initialized dependency
    """
    @abc.abstractmethod
    def __call__(self, event):
        raise NotImplementedError(
            'The processor <{}> must implement __call__'.format(get_qualified_name(self)))  # pragma: no cover


class ConstructorInjection(Base):

    """Responsible for initializing the dependency.

    Responsible for initializing the dependency and injecting any required
    values into the constructor.

    Args:
        event (watson.events.types.Event): The event dispatched from the container.

    Returns:
        mixed: The dependency
    """
    def __call__(self, event):
        definition = event.params['definition']
        item = definition['item']
        args, kwargs = [], {}
        if 'init' in definition:
            init = definition['init']
            if isinstance(init, dict):
                for key, val in init.items():
                    kwargs[key] = get_param_from_container(val, self.container)
            elif isinstance(init, list):
                for arg in init:
                    args.append(get_param_from_container(arg, self.container))
        if definition.get('call_type', None) == FUNCTION_TYPE:
            kwargs['container'] = self.container
        return item(*args, **kwargs)


class SetterInjection(Base):

    """Responsible for injecting required values into setter methods.

    Args:
        event (watson.events.types.Event): The event dispatched from the container.

    Returns:
        mixed: The dependency
    """

    def __call__(self, event):
        item = event.target
        definition = event.params['definition']
        if 'setter' in definition:
            for setter, args in definition['setter'].items():
                method = getattr(item, setter)
                if isinstance(args, dict):
                    kwargs = {arg: get_param_from_container(
                              value,
                              self.container) for arg,
                              value in args.items()}
                    method(**kwargs)
                elif isinstance(args, list):
                    args = [get_param_from_container(arg, self.container)
                            for arg in args]
                    method(*args)
                else:
                    method(get_param_from_container(args, self.container))
        return item


class AttributeInjection(Base):

    """Responsible for injecting required values into attributes.

    Args:
        event (watson.events.types.Event): The event dispatched from the
                                           container.

    Returns:
        mixed: The dependency
    """

    def __call__(self, event):
        item = event.target
        if 'property' in event.params['definition']:
            for prop, value in event.params['definition']['property'].items():
                setattr(
                    item,
                    prop,
                    get_param_from_container(
                        value,
                        self.container))
        return item


class ContainerAware(Base):

    """Injects the container into a dependency.

    Responsible for injecting the container in any class that extends
    watson.di.ContainerAware. The container is then accessible via object.container

    Args:
        event (watson.events.types.Event): The event dispatched from the container.

    Returns:
        mixed: The dependency
    """

    def __call__(self, event):
        item = event.target
        if isinstance(item, di.ContainerAware):
            item.container = self.container
        return item


def get_param_from_container(param, container):
    """Internal function used by the container.

    Retrieve a parameter from the container, and determine whether or not that
    parameter is an existing dependency.

    Returns:
        mixed: The dependency (if param name is the same as a dependency), the
               param, or the value of the param.
    """
    if param in container.params:
        param = container.params[param]
        if param in container:
            param = container.get(param)
    elif param in container:
        param = container.get(param)
    else:
        if isinstance(param, FunctionType):
            param = param(container)
    return param
