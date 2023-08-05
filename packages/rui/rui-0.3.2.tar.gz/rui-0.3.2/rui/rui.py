#!/usr/bin/env python
# -*- coding: utf-8 -*-
from abc import abstractmethod, ABCMeta
from uuid import uuid1
from hashlib import md5
from .exceptions import (DuplicateEntityError, DuplicateSystemError,
                         UnmanagedEntityError, NonUniqueTagError)


class World(object):
    '''
    A World holds all entities, groups, and systems
    '''
    def __init__(self, delta=1):
        self._delta = delta
        self._entities = list()
        self._systems = list()
        self._groups = dict()

    def add_entity(self, entity):
        ''' Add entity to world.
            entity is of type Entity
        '''
        if not entity in self._entities:
            entity.set_world(self)
            self._entities.append(entity)
        else:
            raise DuplicateEntityError(entity)

    def add_entities(self, *entities):
        ''' Add multiple entities to world
            All members of entities are of type Entity
        '''

        for entity in entities:
            entity.set_world(self)
            self.add_entity(entity)

    def add_system(self, system):
        '''
        Add system to the world.
        All systems will be processed on World.process()
        system is of type System
        '''
        if system not in self._systems:
            system.set_world(self)
            self._systems.append(system)
        else:
            raise DuplicateSystemError(system)

    def register_entity_to_group(self, entity, group):
        '''
        Add entity to a group.
        If group does not exist, entity will be added as first member
        entity is of type Entity
        group is a string that is the name of the group
        '''
        if entity in self._entities:
            if group in self._groups:
                self._groups[group].append(entity)
            else:
                self._groups[group] = [entity]
        else:
            raise UnmanagedEntityError(entity)

    def create_entity(self, tag=''):
        '''
        Creates Entity
        (optionally) tag is a string that is the tag of the Entity.
        '''
        return Entity(tag)

    def get_entity_by_tag(self, tag):
        '''
        Get entity by tag
        tag is a string that is the tag of the Entity.
        '''
        matching_entities = list(filter(lambda entity: entity.get_tag() == tag,
                                        self._entities))
        if matching_entities:
            return matching_entities[0]
        else:
            return None

    def get_entities_by_components(self, *components):
        '''
        Get entity by list of components
        All members of components must be of type Component
        '''
        return list(filter(lambda entity:
                           set(map(type, entity.get_components())) ==
                           set(components),
                           self._entities))

    def get_entities(self):
        '''
        Gets all entities
        '''
        return self._entities

    def get_group(self, group):
        '''
        Gets a specific group
        group is the string of a Group
        '''
        return self._groups[group]

    def get_delta(self):
        '''
        Returns delta
        '''
        return self._delta

    def set_delta(self, delta):
        '''
        Sets delta
        '''
        self._delta = delta

    def process(self):
        '''
        Processes entire world and all systems in it
        '''
        for system in self._systems:
            system.process(self._delta)


class Entity(object):
    '''
    Instances of Entity are unique IDs that hold Components.
    (optionally) tag is a string that refers to the entity
    '''
    def __init__(self, tag=''):
        self._tag = tag
        self._uuid = uuid1().int
        self._components = list()

    def set_world(self, world):
        '''
        Sets the world an entity belongs to.
        Checks for tag conflicts before adding.
        '''
        if world.get_entity_by_tag(self._tag) and self._tag != '':
            raise NonUniqueTagError(self._tag)
        else:
            self._world = world

    def get_uuid(self):
        '''
        Returns uuid
        '''
        return self._uuid

    def get_tag(self):
        '''
        Returns tag
        '''
        return self._tag

    def set_tag(self, tag):
        '''
        Sets the tag.
        If the Entity belongs to the world it will check for tag conflicts.
        '''
        if self._world:
            if self._world.get_entity_by_tag(tag):
                raise NonUniqueTagError(tag)
        self._tag = tag

    def add_component(self, component):
        '''
        Adds a Component to an Entity
        '''
        if component not in self._components:
            self._components.append(component)

    def get_component(self, component_type):
        '''
        Gets component of component_type or returns None
        '''
        matching_components = list(filter(lambda component:
                                          isinstance(component,
                                                     component_type),
                                          self._components))
        if matching_components:
            return matching_components[0]
        else:
            return None

    def get_components(self):
        '''
        Returns all components
        '''
        return self._components

    def __str__(self):
        return 'Entity {0}'.format(self.__class__)

    def __repr__(self):
        return '{0} {1}'.format(self.__class__, self._uuid)

    def __eq__(self, other):
        return self.get_uuid() == other.get_uuid()

    def __ne__(self, other):
        return self.get_uuid() != other.get_uuid()

    def __hash__(self):
        return int(md5(self.__repr__()).hexdigest(), 16)


class Component(object):
    def __str__(self):
        return 'Component {0}'.format(self.__class__)

    def __repr__(self):
        return '{0}'.format(self.__class__)

    def __eq__(self, other):
        return type(self) == type(other)

    def __ne__(self, other):
        return type(self) != type(other)

    def __hash__(self):
        return int(md5(self.__repr__()).hexdigest(), 16)


class System(object):
    __metaclass__ = ABCMeta

    def set_world(self, world):
        '''
        Sets the world this system belongs to
        '''
        self.world = world

    @abstractmethod
    def process(self, delta):
        '''Update the system'''

    def __str__(self):
        return 'System {0}'.format(self.__class__)

    def __repr__(self):
        return '{0}'.format(self.__class__)

    def __eq__(self, other):
        return type(self) == type(other)

    def __ne__(self, other):
        return type(self) == type(other)

    def __hash__(self):
        return int(md5(self.__repr__()).hexdigest(), 16)
