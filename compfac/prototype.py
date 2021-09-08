#from typing import NamedTuple
from abc import ABC, abstractmethod
from collections import namedtuple


# Types
Position = namedtuple('Position',
                      ('x',
                       'y'))

BoundingBox = namedtuple('BoundingBox',
                         ('left_top',
                          'right_bottom',
                          'orientation'))
EnergySource = namedtuple('EnergySource',
                          ('type',
                           'buffer_capacity',
                           'usage_priority',
                           'input_flow_limit',
                           'output_flow_limit',
                           'drain',
                           'fuel_inventory_size',
                           'burnt_inventory_size',
                           'effectivity',
                           'fuel_category',
                           'fuel_categories',
                           'fluid_box',
                           'burns_fluid',
                           'scale_fluid_usage',
                           'fluid_usage_per_tick',
                           'maximum_temperature'))

FluidBox = namedtuple('FluidBox',
                      ('pipe_connections',
                       'base_area',
                       'base_level',
                       'height',
                       'filter',
                       'minimum_temperature',
                       'maximum_temperature',
                       'production_type'))

PipeConnectionDefinition = namedtuple('PipeConnectionDefinition',
                                      ('position',
                                       'positions',
                                       'type'))

#Energy = namedtuple('Energy') Energy input needs to be parsed

ModuleSpecification = namedtuple('ModuleSpecification',
                                 ('module_slots'))

EffectTypeLimitation = namedtuple('EffectTypeLimitation',
                                  ('allowed_effects'))

                    
# Prototypes
PrototypeBase = namedtuple('PrototypeBase',
                           ('name',
                            'type'))

Entity = namedtuple('Entity', PrototypeBase._fields +
                    ('collision_box',
                     'collision_mask',
                     'drawing_box',
                     'selection_box',
                     'subgroup'))

EntityWithHealth = namedtuple('EntityWithHealth', Entity._fields +
                              ())

Accumulator = namedtuple('Accumulator', EntityWithHealth._fields +
                         ('charge_cooldown',
                          'discharge_cooldown'))

Beacon = namedtuple('Beacon', EntityWithHealth._fields +
                    ('distribution_effectivity',
                     'energy_source',
                     'energy_usage',
                     'module_specification',
                     'supply_area_distance',
                     'allowed_effects'))

Boiler = namedtuple('Boiler', EntityWithHealth._fields +
                    ('energy_consumption',
                     'energy_source',
                     'fluid_box',
                     'output_fluid_box',
                     'target_temperature'))

BurnerGenerator = namedtuple('BurnerGenerator', EntityWithHealth._fields +
                             ('burner',
                              'energy_source',
                              'max_power_output'))

Container = namedtuple('Container', EntityWithHealth._fields +
                       ('inventory_size',))

LogisticContainer = namedtuple('LogisticContainer', Container._fields +
                               ('logistic_mode',))

CraftingMachine = namedtuple('CraftingMachine', EntityWithHealth._fields +
                             ('crafting_categories',
                              'crafting_speed',
                              'energy_source',
                              'energy_usage',
                              'allowed_effects',
                              'base_productivity',
                              'fluid_boxes',
                              'module_specification'))

AssemblingMachine = namedtuple('AssemblingMachine', CraftingMachine._fields +
                               ('fixed_recipe',))

RocketSilo = namedtuple('RocketSilo', AssemblingMachine._fields +
                        ('active_energy_usage',
                         'idle_energy_usage',
                         'lamp_energy_usage'))

Furnace = namedtuple('Furnace', CraftingMachine._fields +
                     ('result_inventory_size',
                      'source_inventory_size'))

FlyingRobot = namedtuple('FlyingRobot', EntityWithHealth._fields +
                         ('speed',
                          'energy_per_move',
                          'energy_per_tick',
                          'max_energy',
                          'max_speed',
                          'max_to_charge',
                          'min_to_charge',
                          'speed_multiplier_when_out_of_energy'))

RobotWithLogisticInterface = namedtuple('RobotWithLogisticInterface', FlyingRobot._fields +
                                        ('max_payload_size',))

LogisticRobot = namedtuple('LogisticRobot', RobotWithLogisticInterface._fields +
                           ())

Generator = namedtuple('Generator', EntityWithHealth._fields +
                       ('effectivity',
                        'energy_source',
                        'fluid_box',
                        'fluid_usage_per_tick',
                        'maximum_temperature',
                        'burns_fluid',
                        'max_power_output'))




"""
class Material(ABC):
    @abstractmethod
    def isFuel():
        pass
    
    pass


class MyType(ABC):
    @classmethod
    def __subclasshook__(cls, C):
        if cls is MyType:
            if any("type_" in B.__dict__ for B in C.__mro__):
                return True
        return NotImplemented
"""

#Material.register(EntityWithHealth)

"""
Position = NamedTuple('Position',
                      (('x', float),
                       ('y', float)))



BoundingBox = NamedTuple('BoundingBox', get_field_pairs(Position) + 
                         (('left_top', Position),
                          ('right_bottom', Position),
                          ('orientation', float)))
"""
"""
class Position(NamedTuple):
    x: float
    y: float

class BoundingBox(NamedTuple):
    left_top: Position
    right_bottom: Position
    orientation: float = None

class PrototypeBase(NamedTuple):
    name: str
    type: str
"""
#class Entity(PrototypeBase, NamedTuple):
#    collision_box: BoundingBox

"""
# helper functions and helper classes
def get_field_pairs(cls):
    return tuple(zip(list(cls._field_types), list(cls._field_types.values())))

class NoneIter:
    def __iter__(self):
        return self

    def __next__(self):
        return None
"""
