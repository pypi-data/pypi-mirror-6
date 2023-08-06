# -*- coding: utf-8 -*-
from inspect import isclass, isfunction
from watson.common import imports
from watson.common.datastructures import dict_deep_update
from watson.events import dispatcher, types
from watson.di import processors
from watson.di.types import FUNCTION_TYPE, CLASS_TYPE


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


class IocContainer(dispatcher.EventDispatcherAware):
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
    _pre_process_event = None
    _post_process_event = None

    def __init__(self, config=None):
        """Initializes the container and set some default configuration options.

        Args:
            config (dict): The params, definitions and processors.
        """
        self.__instantiated__ = {}
        self.config = dict_deep_update(DEFAULTS, config or {})
        self.__instantiated__ = {}
        self._pre_process_event = types.Event(name=PRE_EVENT)
        self._post_process_event = types.Event(name=POST_EVENT)
        for event, listeners in self.config['processors'].items():
            for processor in listeners:
                self.attach_processor(
                    event,
                    imports.load_definition_from_string(processor)())

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

    def get(self, name):
        """Retrieve a dependency from the container.

        Args:
            name (string): The name of the dependency to retrieve.

        Raises:
            KeyError: If the definition or item within the definition are
                      not specified.

        Returns:
            mixed: The dependency
        """
        if name not in self:
            self.add_definition(name, {'item': name})
        if name in self.__instantiated__:
            return self.__instantiated__[name]
        definition = self.config['definitions'][name]
        instance = None
        obj = None
        if 'call_type' not in definition:
            # definition hasn't be retrieved yet, determine the type of
            # dependency
            obj = self._get_dependency(definition)
            call_type = self._get_type(obj)
            definition['call_type'] = call_type
            if call_type:
                definition['item'] = obj
            else:
                instance = obj
        if definition['call_type']:
            # The dependency needs to be instantiated or called
            instance = self._create_instance(name, definition)
        if (definition.get('type', None) != 'prototype'
                or not definition['call_type']):
            # The dependency should only be retrieved once
            self._add_to_instantiated(name, instance)
        return instance

    def add(self, name, obj, type_='singleton'):
        """Add an instantiated dependency to the container.

        Args:
            name (string): The name used to reference the dependency
            obj (mixed): The dependency to add
            type_ (string): prototype|singleton depending on if it should be
                            instantiated on each IocContainer.get call.
        """
        self._add_to_instantiated(name, obj)
        self.add_definition(name,
                            {'type': type_,
                             'item': imports.get_qualified_name(obj)})

    def add_definition(self, name, definition):
        """Adds a dependency definition to the container.

        Args:
            name (string): The name used to reference the dependency
            definition (dict): The definition of the dependency.
        """
        self.definitions[name] = definition

    # Convenience methods

    @property
    def instantiated(self):
        return self.__instantiated__

    @property
    def params(self):
        """Convenience method for retrieving the params.

        Returns:
            dict: A dict of params.
        """
        return self.config.get('params', {})

    @property
    def definitions(self):
        """Convenience method for retrieving the definitions.

        Returns:
            dict: A dict of params.
        """
        return self.config['definitions']

    # Internals

    def _get_type(self, obj):
        type_ = CLASS_TYPE
        if isfunction(obj):
            type_ = FUNCTION_TYPE
        elif isinstance(obj, (list, tuple, dict, set, str)):
            type_ = None
        return type_

    def _create_instance(self, name, definition):
        params = {'definition': definition, 'name': name}
        self._pre_process_event.target = self
        self._pre_process_event.params = params
        result = self.dispatcher.trigger(self._pre_process_event)
        obj = result.last()
        self._post_process_event.target = obj
        self._post_process_event.params = params
        self.dispatcher.trigger(self._post_process_event)
        return obj

    def _add_to_instantiated(self, name, item):
        self.__instantiated__[name] = item

    def _get_dependency(self, definition):
        """Loads a definition item.
        """
        item = definition['item']
        if isinstance(item, str):
            item = imports.load_definition_from_string(definition['item'])
        return item

    def __contains__(self, name):
        """Determine if the container contains the specific dependency.
        """
        return name in self.definitions

    def __repr__(self):
        return (
            '<{0}: {1} param(s), {2} definition(s)>').format(
            imports.get_qualified_name(self), len(self.params),
            len(self.definitions)
        )
