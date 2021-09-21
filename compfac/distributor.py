from functools import reduce

import numpy as np

from bp import load_blueprint, save_blueprint

# Preprocess the blueprint
# Ensure that all positions starts from index 0, and direction 0 is explicitly stored
def preprocess_bp(bp: dict):
    entities = bp['blueprint']['entities']

    min_x = np.floor(min([e['position']['x'] for e in entities]))
    max_x = np.ceil(max([e['position']['x'] for e in entities]))
    min_y = np.floor(min([e['position']['y'] for e in entities]))
    max_y = np.ceil(max([e['position']['y'] for e in entities]))

    for e in entities:
        p = e['position']
        p['x'] -= min_x
        p['y'] -= min_y

        if e.get('direction') == None:
            e['direction'] = 0
            

# Load the balancer blueprint
bal_bp = load_blueprint("balancer_16_16_asym.base64")
preprocess_bp(bal_bp)
entities = bal_bp['blueprint']['entities']


# Length and height of the blueprint
L = max([e['position']['x'] for e in entities]) + 1
H = max([e['position']['y'] for e in entities]) + 1


# Filter for row n (n is the y coordinate)
row_n = lambda n: list(filter(lambda e: e['position']['y'] == n, entities))
top_row = row_n(H-1)
bottom_row = row_n(0)

# Print the 3rd row in the blue print
r = sorted(row_n(H-9-1), key=lambda e: e['position']['x'])
#print(list(map(lambda e: e['name'], r)))


# Create a mapping from entity number to entity
entities_dict = {e['entity_number']: e for e in entities}


# Object-tile displacement information for common objects
object_tile_disp = {
    'transport-belt': [np.array([0, 0])],
    'underground-belt': [np.array([0, 0])],
    'splitter': [np.array([-0.5, 0]), np.array([0.5, 0])]
}


# Rotate clockwise (or counter clockwise for a RHD coordinate system) 
# 90, 180 and 270 degrees of rotation correspond to `direction` 2, 4 and 6
identity_mat = np.identity(2, dtype=np.int)
rotation_mat = np.array([[0, -1], [1, 0]])
rotation_mat_dict = {d: reduce(lambda x, y: x.dot(y), [rotation_mat] * (d//2), identity_mat) for d in (0, 2, 4, 6)}



# Create a mapping from the grid to entity number
grid = np.zeros([L, H], dtype=np.int)
for e in entities:
    p = e['position']
    x, y = p['x'], p['y']
    p_vec = np.array([x, y])

    direction = e['direction']
    disp = list(map(lambda d: rotation_mat_dict[direction].dot(d),
                    object_tile_disp[e['name']]))
    tiles = list(map(lambda v: v + p_vec, disp))

    for tile in tiles:
        i, j = int(tile[0]), int(tile[1])
        grid[i, j] = e['entity_number']


"""
The axes for the `position` of the entities in a blueprint is different from
the axes we usually use.
Namely, the direction of the y axis is reversed.
"""

"""
on a grid, the directions are:
up: 0
right: 2
down: 4
left: 6
"""
        
# Function to recursively find a strip
direction_disp = {
    0: {'x': 0, 'y': -1},
    2: {'x': 1, 'y': 0},
    4: {'x': 0, 'y': 1},
    6: {'x': -1, 'y': 0}
}  

def next_object(entity_num: int):
    e = entities_dict[entity_num]
    p = e['position']
    x, y = p['x'], p['y']
    disp = direction_disp[e['direction']]
    x_next, y_next = x + disp['x'], y + disp['y']

    if any([x_next < 0,
            x_next >= L,
            y_next < 0,
            y_next >= H
        ]):
        return None

    e_next = grid[x_next, y_next]

    if not entities_dict.get(e_next).get('name') == 'transport-belt':
        return None

    return entities_dict.get(e_next)


def follow_strip(entity_num: int):
    strip = [entity_num]
    while True:
        next_e = next_object(strip[-1])
        if next_e:
            strip.append(next_e['entity_number'])
        else:
            break
    return strip

# Function to find the pairing for an underground belt
def ub_pair(entity_num: int):
    e = entities_dict[entity_num]
    p = e['position']
    x, y = p['x'], p['y']
    direction = e['direction']
    disp = direction_disp[direction]

    if not e['type'] == 'input':
        raise Exception("Not an input underground belt")
        return None

    output = None
    for i in range(1, 6):
        x_next, y_next = x + i * disp['x'], y + i * disp['y']
        if any([x_next < 0,
                x_next >= L,
                y_next < 0,
                y_next >= H
            ]):
            return None
        e_next = grid[x_next, y_next]

        if all([entities_dict[e_next]['name'] == 'underground-belt',
                entities_dict[e_next]['type'] == 'output',
                entities_dict[e_next]['direction'] == e['direction']
                ]):
            output = e_next
            break

    return (entity_num, output)


"""
How do we build the distributor graph?

Representation: 
node name 
-> list of incident nodes

e.g.
E = {
1: [2, 3],
2: [1],
3: [2]
}
c = {
(1, 2): 15,
(1, 3): 15,
(2, 1): 15,
(3, 2): 15
}


Strip: seen as 1 edge
Strip naming: entity number


Splitter: seen as 4 edge intersecting at 1 point, 2 in and 2 out
Splitter node naming: entity number
Splitter edges naming: (entity number, i) (i < 4)


"""

#unvisted = set(entities_dict)

"""
Function that finds an entire strip (including underground belts)

extension(entity_num: int, unvisited: set)

returns 
"""

"""
Function that finds an entire strip (including underground belts)

extension(entity_num: int, unvisited: set)

returns 
"""
