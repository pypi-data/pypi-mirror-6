# -*- coding: utf-8 -*-
from types import FunctionType
from watson.di import processors
from watson.events.dispatcher import EventDispatcherAware
from watson.events.types import Event
from watson.common.datastructures import dict_deep_update
from watson.common.imports import (get_qualified_name,
                                   load_definition_from_string)


PRE_EVENT = 'event.container.pre'
POST_EVENT = 'event.container.post'
DEFAULTS = {
    'params': {},
    'definitions': {},
    'processors': {
        PRE_EVENT: [
            'watson.di.processors.ConstructorInjection',
        ],
        POST_EVENT: [
            'watson.di.processors.SetterInjection',
            'watson.di.processors.AttributeInjection',
            'watson.di.processors.ContainerAware'
        ]
    }
}


class IocContainer(EventDispatcherAware):

    """A simple dependency injection container that can store and retrieve
    dependencies for an application.

    The container is configured via a dict containing the following keys.

    params
        A dict of data that can be injected into a dependency.
        If the value of the key is the same as the name of another
        dependency then the dependency will be referenced.

    definitions
        A dict of definitions that are to be loaded by the container.
        Available keys within a definition are as follows.

            item
                The qualified name of a class or function
            type
                singleton (only load the dependency once) or prototype
                (instantiate and return a new dependency on each request)
            init
                A list or dict of items to be injected into the dependency on
                instantiation.
            setter
                A list or dict of methods to be called upon instantiation.
            property
                Same as setter

        Only 'item' is a required key.

    processors
        A dict of events to be listened for and processors to be called.

    Example:

    .. code-block:: python

        container = IocContainer({
            'params': {
                'db.host': 'localhost'
            },
            'definitions': {
                'database': {
                    'item': 'db.adapters.MySQL'
                    'init': {
                        'host': 'db.host',
                        'username': 'simon',
                        'password': 'test',
                        'db': 'test'
                    }
                }
            }
        })
        db = container.get('database')  # an instance of db.adapters.MySQL

    Attributes:
        config (dict): A dict containing the definitions, params and processors.
        __instantiated__ (dict): A cache of already instantiated dependencies.

    """
    config = None
    __instantiated__ = None

    @property
    def instantiated(self):
        return self.__instantiated__

    @property
    def params(self):
        """Convenience method for retrieving the params.

        Returns:
            dict: A dict of params.
        """
        return self.config['params']

    @property
    def definitions(self):
        """Convenience method for retrieving the definitions.

        Returns:
            dict: A dict of params.
        """
        return self.config['definitions']

    def __init__(self, config=None):
        """Initializes the container and set some default configuration options.

        Args:
            config (dict): A dict containing the params, definitions and processors.
        """
        self.config = dict_deep_update(DEFAULTS, config or {})
        self.__instantiated__ = {}
        for event, listeners in self.config['processors'].items():
            for processor in listeners:
                self.attach_processor(
                    event,
                    load_definition_from_string(processor)())

    def get(self, name):
        """Retrieve a dependency from the container.

        Args:
            name (string): The name of the dependency to retrieve.

        Raises:
            KeyError: If the definition or item within the definition are not specified.

        Returns:
            mixed: The dependency
        """
        definition = self.__find(name)
        if (name in self.__instantiated__
                and definition.get('type', '').lower() == 'singleton'
                and not isinstance(self.__instantiated__.get(name),
                                   FunctionType)):
            instantiated = self.__instantiated__[name]
        else:
            instantiated = self.__create_instance(name, definition)
            self.__instantiated__[name] = instantiated
        return instantiated

    def add(self, name, item, type='singleton', **kwargs):
        """Add a dependency to the container (either already instatiated or not).

        Args:
            name (string): The name used to reference the dependency
            item (mixed): The dependency to add (either qualified name or instance)
        """
        definition = self.definitions.get(name, {'item': item, 'type': type})
        definition.update(**kwargs)
        self.definitions[name] = definition
        if not isinstance(item, str):
            self.__instantiated__[name] = item

    def __contains__(self, dependency):
        """Returns whether or not a dependency is defined in the container.

        Args:
            dependency (string): The name of the dependency to find.
        """
        return dependency in self.definitions

    def __find(self, name):
        """
        Attempts to retrieve a definition from the container configuration. If
        no definition is found, it will attempt to add the requested dependency
        to the container.
        """
        definitions = self.definitions
        if name not in definitions:
            self.add(name, name)
            definitions = self.definitions
        definition = definitions[name]
        if 'item' not in definition:
            raise KeyError('item not specified in dependency definition')
        definition['type'] = definition.get('type', 'singleton').lower()
        return definition

    def __create_instance(self, name, definition):
        params = {
            'definition': definition,
            'dependency': name
        }
        pre_process_event = Event(
            name=PRE_EVENT,
            target=definition,
            params=params)
        result = self.dispatcher.trigger(pre_process_event)
        dependency = result.last()
        post_process_event = Event(
            name=POST_EVENT,
            target=dependency,
            params=params)
        self.dispatcher.trigger(post_process_event)
        return dependency

    def attach_processor(self, event, processor):
        """Attach a processor to the container.

        Attaches a processor to the container that will be triggered on a specific
        event.

        Args:
            event (string): The name of the event (watson.di.container.POST_EVENT or PRE_EVENT)
            processor (watson.di.processors.BaseProcessor): The processor to attach.
        """
        if not isinstance(processor, processors.Base):
            raise TypeError(
                'Processor must be of type {0}'.format(processors.Base))
        processor.container = self
        self.dispatcher.add(event, processor)

    def __repr__(self):
        return ('<{0}: {1} param(s), '
                '{2} definition(s)>').format(
            get_qualified_name(self), len(self.config['params']),
            len(self.config['definitions']))
