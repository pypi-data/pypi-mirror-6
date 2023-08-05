===============================
rui (叡)
===============================

.. image:: https://badge.fury.io/py/rui.png
    :target: http://badge.fury.io/py/rui
    
.. image:: https://travis-ci.org/timothyhahn/rui.png?branch=master
        :target: https://travis-ci.org/timothyhahn/rui

.. image:: https://pypip.in/d/rui/badge.png
        :target: https://crate.io/packages/rui?version=latest


An imperfect Python ECS

* Free software: BSD license
* Documentation: http://rui.rtfd.org.

Features
--------

* A simple Python Entity Component System
* Unoptimized
* Favors World based access, eschews Managers (Artemis, which inspired this, uses both)
* To learn more about Entity Component Systems
    * http://www.gamedev.net/page/resources/_/technical/game-programming/understanding-component-entity-systems-r3013
    * http://www.randygaul.net/2013/05/20/component-based-engine-design/
    * http://gamadu.com/artemis/manual.html

Installation
--------

.. code:: bash

    $ pip install rui
        

Usage
--------
.. code:: python

    ## Import rui
    from rui.rui import Component, System, World

    ## Define Components
    class Position(Component):
        def __init__(self, x, y):
            self.x = x
            self.y = y

    class Velocity(Component):
        def __init__(self, x, y):
            self.x = x
            self.y = y

    ## Define System
    class MovementSystem(System):
        def process(self, delta): ## This method is a minimal requirement
            entities = self.world.get_entities_by_components(Position, Velocity)

            for entity in entities:
                position = entity.getComponent(Position)
                velocity = entity.getComponent(Velocity)
                position.x += velocity.x * delta
                position.y += velocity.y * delta

    ## Create the world and set up Entities
    world = World()

    player = world.create_entity(tag='PLAYER') # This does not automatically add the entity to the world
                                   # You could also do player = Entity('PLAYER')
                                   # tag is completely optional, but it allows you to look up this entity later
    player.add_component(Position(0,0))
    player.add_component(Velocity(0,0))
    world.add_entity(player)
    
    world.add_system(MovementSystem())
    
    while True:
        ## Get Player Inputs
        player_by_tag = world.get_entity_by_tag('PLAYER') ## Get the entity by its tag
        world.process() ## The world will step through its motions
