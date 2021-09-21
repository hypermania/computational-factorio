import json
import copy
from slpp import slpp as lua
import numpy as np
from math import ceil, floor

# Load data

dat_folder = "recipe-lister-6"

item = json.load(open(dat_folder + "/item.json", "r"))
fluid = json.load(open(dat_folder + "/fluid.json", "r"))
recipe = json.load(open(dat_folder + "/recipe.json", "r"))
resource = json.load(open(dat_folder + "/resource.json", "r"))
ass = json.load(open(dat_folder + "/assembling-machine.json", "r"))
mining = json.load(open(dat_folder + "/mining-drill.json", "r"))
furnace = json.load(open(dat_folder + "/furnace.json", "r"))

raw = lua.decode(open("py_data_6.lua", "r").read())


# Preprocess data

mat_exclusion_list = [
    'blueprint',
    'deconstruction-planner',
#    'ore-eraser',
    'upgrade-planner',
    'blueprint-book',
    'selection-tool',
    'copy-paste-tool',
    'cut-paste-tool'
]
for mat in mat_exclusion_list:
    del item[mat]

recipe_exclusion_list = [ # disabled recipes
    'crushing-iron',
    'crushing-copper',
    'dedicated-syngas-from-hydrogen-1',
    'raw-borax',
#    'hotair-nexelit-plate'
    'urea',
    'urea2',
    'advanced-oil-processing',
    'basic-oil-processing',
    'heavy-oil-cracking',
    'light-oil-cracking',
    'plastic-bar',
    'starch',
    'starch-2',
    'fawogae',
    'fawogae2'
] + [ # locked recipes
] + [ # recipes I don't want to use
]

for r in recipe.values():
    if r['category'] == 'space-cottongut':
        recipe_exclusion_list.append(r['name'])
    if r['category'] == 'rocket-mk01':
        recipe_exclusion_list.append(r['name'])
    if r['category'] == 'handcrafting':
        recipe_exclusion_list.append(r['name'])
    if r['category'] == 'converter-valve':
        recipe_exclusion_list.append(r['name'])
        
for r in recipe_exclusion_list:
    del recipe[r]


resource_exclusion_list = [
]
for r in resource_exclusion_list:
    del resource[r]


ass_exclusion_list = [
    'crash-site-assembling-machine-1-repaired',
#    'crash-site-assembling-machine-2-repaired'
]
for m in ass_exclusion_list:
    del ass[m]


# Index of materials
index_mat = {}
item_list = list(item.values())
for i in range(0, len(item)):
    index_mat[item_list[i]['name']] = i
fluid_list = list(fluid.values())
for i in range(0, len(fluid)):
    index_mat[fluid_list[i]['name']] = len(item) + i

ass_list = list(ass.values())
mining_list = list(mining.values())
furnace_list = list(furnace.values())
speed_dict = dict({m['name']:m['crafting_speed'] for m in ass_list},
                  **{m['name']:m['mining_speed'] for m in mining_list},
                  **{m['name']:m['crafting_speed'] for m in furnace_list})
slot_dict = dict({m['name']:m['module_inventory_size'] for m in ass_list},
                 **{m:(raw['mining-drill'][m]['module_specification']['module_slots'] if ('module_specification' in raw['mining-drill'][m]) else 0) for m in mining},
                 **{m['name']:m['module_inventory_size'] for m in furnace_list})
slot_dict['rocket-silo'] = raw['rocket-silo']['rocket-silo']['module_specification']['module_slots']

for r in raw['rocket-silo'].values():
    speed_dict[r['name']] = r['crafting_speed']

category_dict = {}
for m in ass_list:
    for c in m['crafting_categories']:
        if c not in category_dict:
            category_dict[c] = set()
            category_dict[c].add(m['name'])
        else:
            category_dict[c].add(m['name'])
for m in mining_list:
    for c in m['resource_categories']:
        if c not in category_dict:
            category_dict[c] = set()
            category_dict[c].add(m['name'])
        else:
            category_dict[c].add(m['name'])
for m in furnace_list:
    for c in m['crafting_categories']:
        if c not in category_dict:
            category_dict[c] = set()
            category_dict[c].add(m['name'])
        else:
            category_dict[c].add(m['name'])
for m in raw['rocket-silo'].values():
    for c in m['crafting_categories']:
        if c not in category_dict:
            category_dict[c] = set()
            category_dict[c].add(m['name'])
        else:
            category_dict[c].add(m['name'])

entity_category_list = [
    'assembling-machine',
    'mining-drill',
    'furnace',
    'rocket-silo',
    'roboport',
    'inserter',
    'accumulator',
    'beacon',
    'boiler',
    'burner-generator',
    'container',
    'electric-pole',
    'generator',
    'heat-pipe',
    'lab',
    'loader',
    'logistic-container',
    'offshore-pump',
    'pipe',
    'pipe-to-ground',
    'pump',
    'radar',
    'solar-panel',
    'splitter',
    'storage-tank',
    'straight-rail',
    'transport-belt',
    'underground-belt'
]
box_dict = {}
collision_dict = {}
for cat in entity_category_list:
    for m in raw[cat].values():
        box = m['selection_box']
        if type(box) == list:
            box_dict[m['name']] = box
        collision_box = m.get('collision_box')
        if collision_box is not None and type(collision_box) == list:
            collision_dict[m['name']] = collision_box

# Manual changes
box_dict['offshore-pump'] = [[-0.5, -1.49], [0.5, 0.49000000000000005]]

dimensions_dict = {m:(ceil(box_dict[m][1][0] - box_dict[m][0][0]), ceil(box_dict[m][1][1] - box_dict[m][0][1])) for m in box_dict}
area_dict = {m:(dimensions_dict[m][0] * dimensions_dict[m][1]) for m in dimensions_dict}

normalized_box_dict = {ent: [[floor(box_dict[ent][0][0] * 2) / 2, floor(box_dict[ent][0][1] * 2) / 2],[ceil(box_dict[ent][1][0] * 2) / 2, ceil(box_dict[ent][1][1] * 2) / 2]] for ent in box_dict}
center_dict = {ent: [-normalized_box_dict[ent][0][0],-normalized_box_dict[ent][0][1]] for ent in normalized_box_dict}



# Specifying assembly machine tiers

#category_speed = {c:min([speed_dict[m] for m in category_dict[c]]) for c in category_dict}
#category_area = {c:min([area_dict[m] for m in category_dict[c]]) for c in category_dict}

category_choice = {}
for c in category_dict:
    choices = category_dict[c]
    #choices_list = list(choices)
    #choices_list.sort(key=lambda k: speed_dict[k])
    #category_choice[c] = choices_list[0]
    for m in choices:
        if len(choices) == 1:
            category_choice[c] = m
        if 'mk02' in m:
            category_choice[c] = m
category_choice['smelting'] = 'electric-furnace'
category_choice['basic-solid'] = 'electric-mining-drill'
category_choice['cooling'] = 'cooling-tower-mk02'
category_choice['fawogae'] = 'fawogae-plantation-mk02'
category_choice['crafting'] = 'assembling-machine-2'
category_choice['basic-crafting'] = 'assembling-machine-2'
category_choice['advanced-crafting'] = 'assembling-machine-2'
category_choice['crafting-with-fluid'] = 'assembling-machine-2'
category_choice['oil-mk01'] = 'oil-derrick-mk01'
category_choice['oil-mk02'] = 'oil-derrick-mk02'
category_choice['oil-mk03'] = 'oil-derrick-mk03'
category_choice['oil-mk04'] = 'oil-derrick-mk04'

category_speed = {c:speed_dict[category_choice[c]] for c in category_dict}
category_area = {c:area_dict[category_choice[c]] for c in category_dict}

"""
TODO: Add recipes from water pumpjack, boiler.
"""

# Adding modules

#speed_bonus_category = {}
prod_list = [r for r in raw['module']['productivity-module-2']['limitation'] if r not in recipe_exclusion_list]
#prod_list = []
prod_list = list(filter(lambda r: r in recipe, prod_list))

for r in prod_list:
    if category_choice[recipe[r]['category']] in ass:
        if ass[category_choice[recipe[r]['category']]]['allowed_effects']['productivity'] == False:
            continue
    r_with_prod = copy.deepcopy(recipe[r])
    slots = slot_dict[category_choice[r_with_prod['category']]]
    prod_bonus = slots * 0.06
    speed_bonus = max(1 - slots * 0.15, 0.2)
    r_with_prod['name'] += '(prod)'
    for mat in r_with_prod['products']:
        mat['amount'] *= 1 + prod_bonus
#    r_with_prod['energy'] /= speed_bonus
    recipe[r_with_prod['name']] = r_with_prod


"""
stat = {}
stat_2 = {}
for ent in collision_dict:
    box = box_dict[ent]
    #box = collision_dict[ent]

    if box[0][0] != -box[1][0]:
        print("horizontally asymmetric: {}".format(ent))
    if box[0][1] != -box[1][1]:
        print("vertically asymmetric: {}".format(ent))

    diff = ceil(box[1][0] - box[0][0]) - (box[1][0] - box[0][0])
    if diff not in stat:
        stat[diff] = 0
    stat[diff] += 1

    diff_2 = (box[1][0] - box[0][0]) - floor(box[1][0] - box[0][0])
    if diff_2 not in stat_2:
        stat_2[diff_2] = 0
    stat_2[diff_2] += 1

    #if diff < 0.21:
    #    print(ent)

    if diff_2 == 0.5:
        print(ent)
"""
