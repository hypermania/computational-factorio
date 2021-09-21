import json
import copy
from slpp import slpp as lua
import numpy as np
from math import ceil, floor
from functools import reduce

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches

from helper import print_recipe
import bp
from preprocess import item, fluid, recipe, resource, ass, furnace, raw, dimensions_dict, box_dict, slot_dict, collision_dict, normalized_box_dict, center_dict

"""
robot_speed = raw['logistic-robot']['py-logistic-robot-02']['speed'] * 60
avg_dist = 30.0
request_amount_multiplier = 2.0
throughput = 10.0
request_amount = throughput / (1 / (avg_dist / robot_speed))
"""


# Load Sample Blueprints

bp_1 = bp.load_blueprint('Blueprints/1.base64')
bp_2 = bp.load_blueprint('Blueprints/2.base64')
bp_3 = bp.load_blueprint('Blueprints/3.base64')
bp_4 = bp.load_blueprint('Blueprints/4.base64')
bp_5 = bp.load_blueprint('Blueprints/5.base64')
bp_6 = bp.load_blueprint('Blueprints/6.base64')
bp_7 = bp.load_blueprint('Blueprints/7.base64')
bp_8 = bp.load_blueprint('Blueprints/8.base64')
bp_9 = bp.load_blueprint('Blueprints/9.base64')


"""
In a usual 2D coordinate system, the x-axis is horizontal pointing left,
and the y-axis is vertical pointing up.
However, in Factorio blueprints, the direction of the y-axis is reversed,
so the y-axis points down.
This means the Factorio coordinate system is left-handed:
when we rotate a vector in Factorio coordinates using the usual counter-clockwise
rotation matrix, we see a clockwise rotation on Factorio screen.

Factorio blueprints denote orientation of entities (machines, inserters, pumps, etc)
via numbers: 0, 2, 4, 6.
In Factorio coordinates, the directions point to directions:
0: (0, 1)
2: (-1, 0)
4: (0, -1)
6: (1, 0)

On Factorio screen, 0->2->4->6 looks like clockwise rotation, 
with the 4 directions being down->left->up->right.
To encode the 0->2->4->6 rotation in Factorio coordinates,
we use the counter-clockwise rotation matrix for RHD coordinate systems:
R = [[0, -1], [1, 0]].
"""

# Rotate clockwise (or counter clockwise for a RHD coordinate system) 
# 90, 180 and 270 degrees of rotation correspond to `direction` 2, 4 and 6
identity_mat = np.identity(2, dtype=np.int)
rotation_mat = np.array([[0, -1], [1, 0]])
rotation_mat_dict = {d: reduce(lambda x, y: x.dot(y), [rotation_mat] * (d//2), identity_mat) for d in (0, 2, 4, 6)}


def bp_collision_test(blueprint):
    entities = blueprint['blueprint']['entities']
    for i in range(0, len(entities)):
        for j in range(i+1, len(entities)):
            if ent_pair_collision_test(entities[i], entities[j]):
                print(entities[i])
                print(entities[j])
                return True
    return False



def ent_pair_collision_test(ent_1, ent_2):
    ent_1_box = normalized_box_dict[ent_1['name']]
    ent_2_box = normalized_box_dict[ent_2['name']]

    ent_1_direction = ent_1.get('direction', 0)
    ent_2_direction = ent_2.get('direction', 0)

    ent_1_bl = np.array([ent_1_box[0][0], ent_1_box[0][1]])
    ent_1_br = np.array([ent_1_box[1][0], ent_1_box[0][1]])
    ent_1_tr = np.array([ent_1_box[1][0], ent_1_box[1][1]])
    ent_1_tl = np.array([ent_1_box[0][0], ent_1_box[1][1]])
    
    ent_2_bl = np.array([ent_2_box[0][0], ent_2_box[0][1]])
    ent_2_br = np.array([ent_2_box[1][0], ent_2_box[0][1]])
    ent_2_tr = np.array([ent_2_box[1][0], ent_2_box[1][1]])
    ent_2_tl = np.array([ent_2_box[0][0], ent_2_box[1][1]])

    ent_1_rotated_bounds = [rotation_mat_dict[ent_1_direction] @ r
                            for r in [ent_1_bl,
                                      ent_1_br,
                                      ent_1_tr,
                                      ent_1_tl]]
    ent_2_rotated_bounds = [rotation_mat_dict[ent_2_direction] @ r
                            for r in [ent_2_bl,
                                      ent_2_br,
                                      ent_2_tr,
                                      ent_2_tl]]

    for i in range(0, int(ent_1_direction/2)):
        temp_r = ent_1_rotated_bounds[0]
        del ent_1_rotated_bounds[0]
        ent_1_rotated_bounds.append(temp_r)
    for i in range(0, int(ent_2_direction/2)):
        temp_r = ent_2_rotated_bounds[0]
        del ent_2_rotated_bounds[0]
        ent_2_rotated_bounds.append(temp_r)
    
    ent_1_x1 = ent_1['position']['x'] + ent_1_rotated_bounds[0][0]
    ent_1_x2 = ent_1['position']['x'] + ent_1_rotated_bounds[2][0]
    ent_1_y1 = ent_1['position']['y'] + ent_1_rotated_bounds[0][1]
    ent_1_y2 = ent_1['position']['y'] + ent_1_rotated_bounds[2][1]
    
    ent_2_x1 = ent_2['position']['x'] + ent_2_rotated_bounds[0][0]
    ent_2_x2 = ent_2['position']['x'] + ent_2_rotated_bounds[2][0]
    ent_2_y1 = ent_2['position']['y'] + ent_2_rotated_bounds[0][1]
    ent_2_y2 = ent_2['position']['y'] + ent_2_rotated_bounds[2][1]

    if ent_1_x2 <= ent_2_x1 or ent_2_x2 <= ent_1_x1:
        return False
    if ent_1_y2 <= ent_2_y1 or ent_2_y2 <= ent_1_y1:
        return False
    return True

# Design Class

empty_blueprint = {'blueprint': {'icons': [{'signal': {'type': 'item', 'name': 'py-roboport-mk01'}, 'index': 1}], 'entities': [], 'item': 'blueprint', 'version': 281474976710656}}

#skeleton = bp.decode('0eJylkd1qwzAMhV+l+HoJdeL8rK9SynA204omsnGU0hD87pOdwQql0NK7cyT508FaRNdPxnlAErvNIuDb4shqv4gRjqj7VKXZGRYCyAziYyNQD8nTNLmT15nrNZImsJgN520hAs8A/pgrD8lwYGeQgMD8oZObv3AaOuPjzA3TzZm3nXXWU4TJuM/ZESI9hYnQrJR5xY2ZdVupvAq88p5bvMVt5SNu+TJXPRNXvYNd08a/TldixP9luXgxflyfFq1Ujfps6kZu66oO4ReKH5yy')

skeleton = {'blueprint': {'icons': [{'signal': {'type': 'item', 'name': 'py-roboport-mk01'}, 'index': 1}], 'entities': [{'entity_number': 1, 'name': 'py-roboport-mk01', 'position': {'x': -31.5, 'y': 854.5}}, {'entity_number': 2, 'name': 'py-roboport-mk01', 'position': {'x': -31.5, 'y': 881.5}}, {'entity_number': 3, 'name': 'py-roboport-mk01', 'position': {'x': -4.5, 'y': 854.5}}, {'entity_number': 4, 'name': 'py-roboport-mk01', 'position': {'x': -4.5, 'y': 881.5}}], 'item': 'blueprint', 'version': 281474976710656}}


class Design():
    """
    blueprint = None
    entities = None
    new_entity_id = None

    pos_entity_map = {}
    entity_obj_map = {}
    """
    
    def __init__(self, base_bp=None):
        if base_bp == None:
            self.blueprint = copy.deepcopy(empty_blueprint)
        else:
            self.blueprint = base_bp
        self.entities = self.blueprint['blueprint']['entities']
        self.pos_entity_map = {}
        self.entity_obj_map = {}
        
        if len(self.entities) > 0:
            self.new_entity_id = max([e['entity_number'] for e in self.entities]) + 1
        else:
            self.new_entity_id = 1

    
    # wrapper for __init__
    def clear(self):
        self.__init__()

    
    # only use this to get new_entity_id
    def get_new_entity_id(self):
        temp = self.new_entity_id
        self.new_entity_id += 1
        return temp

    
    # name is entity name
    # position is the coordinate of the bottom-left corner of the entity (in RHD coord)
    # returns the entity_number of the new entity,
    # or None if the addition cannot be done due to overlap
    def add_entity(self, name:str, position, **options):
        x0, y0 = position
        w, h = dimensions_dict[name]

        # Check for overlap in Blueprint
        for x in range(x0, x0 + w):
            for y in range(y0, y0 + h):
                if (x, y) in self.pos_entity_map:
                    return None

        new_entity = {'entity_number': self.get_new_entity_id(),
                      'name': name,
                      'position': {'x': x0 + center_dict[name][0],
                                   'y': y0 + center_dict[name][1]},
                      **options} # only copies options, does not do deepcopy
        
        # Set pos_entity_map
        for x in range(x0, x0 + w):
            for y in range(y0, y0 + h):
                self.pos_entity_map[(x, y)] = new_entity['entity_number']
        
        self.entity_obj_map[new_entity['entity_number']] = new_entity
        
        self.entities.append(new_entity)
        
        return new_entity['entity_number']

    
    def del_entity(self, entity_num):
        entity = self.entity_obj_map[entity_num]
        name = entity['name']
        
        x0 = int(entity['position']['x'] - center_dict[name][0])
        y0 = int(entity['position']['y'] - center_dict[name][1])
        w, h = dimensions_dict[name]
        for x in range(x0, x0 + w):
            for y in range(y0, y0 + h):
                del self.pos_entity_map[(x, y)]
        
        del self.entity_obj_map[entity_num]
        
        self.entities.remove(entity)

    
    def add_recipe_at_origin(self, recipe_name:str, machine_name:str, **options):
        options_full = {'recipe': recipe_name,
                        **options}
        new_entity_num = self.add_entity(machine_name, (0, 0), **options_full)
        
        return new_entity_num

    
    def add_inserter(self, inserter_name:str, direction:int, position, **options):
        options_full = {'direction': direction,
                        **options}
        new_entity_num = self.add_entity(inserter_name, position, **options_full)
        
        return new_entity_num

    def add_logistic_chest(self, chest_name:str, position, **options):
        options_full = {**options}
        new_entity_num = self.add_entity(chest_name, position, **options_full)
        
        return new_entity_num

    
    def add_solid_input_to_machine(self, entity_number:int, **options):
        machine_name = self.entity_obj_map[entity_number]['name']
        recipe_name = self.entity_obj_map[entity_number]['recipe']
        x_c = self.entity_obj_map[entity_number]['position']['x']
        y_c = self.entity_obj_map[entity_number]['position']['y']
        x, y = int(x_c - center_dict[machine_name][0]), int(y_c - center_dict[machine_name][1])
        
        inserter_pos = (x, y - 1)
        chest_pos = (x, y - 2)

        inserter_num = self.add_inserter('stack-inserter', 0, inserter_pos)
        chest_num = self.add_logistic_chest('logistic-chest-requester', chest_pos)
        
        return (inserter_num, chest_num)


    def add_pipe_to_machine(self, entity_number:int, **options):
        machine_name = self.entity_obj_map[entity_number]['name']
        recipe_name = self.entity_obj_map[entity_number]['recipe']
        x_c = self.entity_obj_map[entity_number]['position']['x']
        y_c = self.entity_obj_map[entity_number]['position']['y']
        x, y = int(x_c - center_dict[machine_name][0]), int(y_c - center_dict[machine_name][1])
        
        return None

    
    def duplicate(self, entity_numbers:list, **options):
        return None
    
    
    def bounding_box(self):
        if len(self.pos_entity_map) > 0:
            x_coords, y_coords = zip(*self.pos_entity_map.keys())
            return (min(x_coords), max(x_coords), min(y_coords), max(y_coords))
        else:
            return None

    
    def bounding_box_dim(self):
        if len(self.pos_entity_map) > 0:
            x_coords, y_coords = zip(*self.pos_entity_map.keys())
            return (max(x_coords) - min(x_coords), max(y_coords) - min(y_coords))
        else:
            return None


    def export(self):
        return bp.encode(self.blueprint)


# Test
d = Design()
print(d.add_entity('pipe', (0, 0)))
print(d.add_entity('pipe', (0, 1)))
print(d.add_entity('pipe', (0, 2)))
print(d.add_entity('pipe', (0, 3)))
print(d.add_entity('pipe', (0, 4)))
d.del_entity(1)

e = Design()
machine_num = e.add_recipe_at_origin('Extract Ulric lard', 'slaughterhouse-mk02')
e.add_solid_input_to_machine(machine_num)

"""
print(d.entities)
print(d.pos_entity_map)
print(d.entity_obj_map)
print()
d.del_entity(1)
print(d.entities)
print(d.pos_entity_map)
print(d.entity_obj_map)
print()
d.add_recipe('sodium-sulfate-1', 'chemical-plant', items={'speed-module': 3})
print(d.entities)
print(d.pos_entity_map)
print(d.entity_obj_map)
"""
"""
def test(name, **options):
    print(name)
    for option in options:
        print("{} = {}".format(option, options[option]))


options1 = {'abc': 5}
options2 = {'def': 6, 'pos': {'x': 1, 'y': 2}}
d = {**options1, **options2}
e = {*options1}
"""
"""
class FloorPlanner(Design):
    L = 0
    W = 0
    grid = None

    def __init__(self, L=10, W=10):
        self.L = L
        self.W = W
        self.grid = np.zeros([L, W], dtype=np.int)


class ModulePlanner(Design):
    L = 0
    W = 0
    grid = None

    def __init__(self, base_bp=None, L=10, W=10):
        Design.__init__(self, base_bp=base_bp)
        self.L = L
        self.W = W
        self.grid = np.zeros([L, W], dtype=np.int)
"""


def round_to_next_pow_2(x:int):
    return 1 << int(x).bit_length()

"""
Bitmap representation of a 2D grid.
The unpacked 2D grid is given by np.unpackbits(self.grid, axis=1).
unpacked_grid[x, y] = 1 or 0, x < W, y < H.
W and H must be mutiples of 8.
W > 0, H > 0.
"""
class BitGrid():
    W = 0
    H = 0
    grid = None

    def __init__(self):
        self.W = 8
        self.H = 8
        #grid_unpacked = np.zeros((self.W, self.H), dtype=np.uint8)
        #self.grid = np.packbits(grid_unpacked, axis=1)
        self.grid = np.zeros((self.W, self.H // 8), dtype=np.uint8)
        
    def extend_grid(self, new_x, new_y):
        if new_x < self.W and new_y < self.H:
            return
        new_W = max(round_to_next_pow_2(new_x), self.W)
        new_H = max(round_to_next_pow_2(new_y), self.H)
        delta_W = new_W - self.W
        delta_H = new_H - self.H

        if delta_H > 0:
            H_zeros = np.zeros((self.W, delta_H // 8), dtype=np.uint8)
            self.grid = np.hstack((self.grid, H_zeros))
        if delta_W > 0:
            W_zeros = np.zeros((delta_W, new_H // 8), dtype=np.uint8)
            self.grid = np.vstack((self.grid, W_zeros))

        self.W = new_W
        self.H = new_H

    def __getitem__(self, key):
        self.extend_grid(key[0], key[1])
        #return np.unpackbits(self.grid, axis=1)[key[0], key[1]]
        byte = self.grid[key[0], key[1] // 8]
        shift = key[1] % 8
        return 1 if (128 >> shift) & byte else 0

    def __setitem__(self, key, value):
        self.extend_grid(key[0], key[1])
        #grid_unpacked = np.unpackbits(self.grid, axis=1)
        #grid_unpacked[key[0], key[1]] = value
        #self.grid = np.packbits(grid_unpacked, axis=1)
        byte = self.grid[key[0], key[1] // 8]
        byte |= 128 >> (key[1] % 8)
        self.grid[key[0], key[1] // 8] = byte

    def __repr__(self):
        grid_unpacked = np.unpackbits(self.grid, axis=1)
        grid_repr = np.flip(grid_unpacked.transpose(), axis=0)
        return str(grid_repr)

    # Returns the bounding box in terms of ((x_min, x_max), (y_min, y_max))
    def bounds(self):
        grid_unpacked = np.unpackbits(self.grid, axis=1)
        x_array, y_array = np.nonzero(grid_unpacked)
        if len(x_array) == 0:
            return None
        return ((min(x_array), max(x_array)+1), (min(y_array), max(y_array)+1))

    # Shift the BitGrid by some amount
    def shift(self, delta_x, delta_y):
        bounds = self.bounds()
        if bounds[0][0] + delta_x < 0 or bounds[1][0] + delta_y < 0:
            return None
        new_W = max(round_to_next_pow_2(bounds[0][1] + delta_x - 1), self.W)
        new_H = max(round_to_next_pow_2(bounds[1][1] + delta_y - 1), self.H)
        grid_unpacked = np.unpackbits(self.grid, axis=1)
        unpadded_grid = grid_unpacked[bounds[0][0]:bounds[0][1], bounds[1][0]:bounds[1][1]]
        padded_grid = np.pad(unpadded_grid,
                             ((bounds[0][0] + delta_x, new_W - bounds[0][1] - delta_x),
                              (bounds[1][0] + delta_y, new_H - bounds[1][1] - delta_y)),
                             constant_values=0)
        result = BitGrid()
        result.grid = np.packbits(padded_grid, axis=1)
        result.W = new_W
        result.H = new_H

        return result
    
    @staticmethod
    def box(w, h, x=0, y=0):
        box = BitGrid()
        box.extend_grid(x+w-1, y+h-1)
        unpacked_box = np.pad(np.ones((w, h), dtype=np.uint8),
                              ((x, box.W - x - w), (y, box.H - y - h)),
                              constant_values=0)
        packed_box = np.packbits(unpacked_box, axis=1)
        box.grid = packed_box
        return box

    def __or__(self, other):
        result = BitGrid()
        new_W = max(self.W, other.W)
        new_H = max(self.H, other.H)
        self.extend_grid(new_W-1, new_H-1)
        other.extend_grid(new_W-1, new_H-1)
        result.extend_grid(new_W-1, new_H-1)
        result.grid = np.bitwise_or(self.grid, other.grid)
        return result
    
    def __ior__(self, other):
        new_W = max(self.W, other.W)
        new_H = max(self.H, other.H)
        self.extend_grid(new_W-1, new_H-1)
        other.extend_grid(new_W-1, new_H-1)
        self.grid = np.bitwise_or(self.grid, other.grid)
        return self

    def __and__(self, other):
        result = BitGrid()
        new_W = max(self.W, other.W)
        new_H = max(self.H, other.H)
        self.extend_grid(new_W-1, new_H-1)
        other.extend_grid(new_W-1, new_H-1)
        result.extend_grid(new_W-1, new_H-1)
        result.grid = np.bitwise_and(self.grid, other.grid)
        return result
    
    def __iand__(self, other):
        new_W = max(self.W, other.W)
        new_H = max(self.H, other.H)
        self.extend_grid(new_W-1, new_H-1)
        other.extend_grid(new_W-1, new_H-1)
        self.grid = np.bitwise_and(self.grid, other.grid)
        return self

    def is_empty(self):
        return not np.any(self.grid)


#box = BitGrid().box(5,5,x=10,y=5)
    
#Try to test bounds(box) using random input data
"""
import random
for i in range(0, 1000):
    w, h = random.randint(1,50), random.randint(1,50)
    x, y = random.randint(0,50), random.randint(0,50)
    g = BitGrid.box(w, h, x=x, y=y)
    assert g.bounds() == ((x, x+w), (y, y+h))
"""
