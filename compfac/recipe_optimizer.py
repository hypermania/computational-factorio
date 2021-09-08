import json
import io
import copy
from slpp import slpp as lua


# Load data

item = json.load(open("recipe-lister-3/item.json", "r"))

fluid = json.load(open("recipe-lister-3/fluid.json", "r"))

recipe = json.load(open("recipe-lister-3/recipe.json", "r"))

resource = json.load(open("recipe-lister-3/resource.json", "r"))

ass = json.load(open("recipe-lister-3/assembling-machine.json", "r"))

mining = json.load(open("recipe-lister-3/mining-drill.json", "r"))

furnace = json.load(open("recipe-lister-3/furnace.json", "r"))

raw = lua.decode(open("py_data_3.lua", "r").read())


# Preprocess data

mat_exclusion_list = [
    'blueprint',
    'deconstruction-planner',
    'ore-eraser',
    'upgrade-planner',
    'blueprint-book',
    'selection-tool',
    'copy-paste-tool',
    'cut-paste-tool'
]
for mat in mat_exclusion_list:
    del item[mat]

recipe_exclusion_list = [
    'crushing-iron',
    'crushing-copper',
#    'molten-iron-01',
#    'molten-iron-02',
#    'sinter-iron-2',
#    'sinter-iron-1',
#    'sinter-copper-1',
#    'sinter-copper-2',
#    'molten-copper-01',
#    'hotair-nexelit-plate-1',
#    'sinter-chromium',
#    'sinter-nickel-1',
#    'sinter-nickel-2',
#    'reduction-nickel',
#    'pa-oxygen',
#    'molten-nickel-02-2',
#    'molten-nickel-03',
#    'grade-2-chromite-pyvoid'
    'sinter-zinc-2',
    'sinter-zinc-1',
    'reduced-zinc',
    'heavy-oil-combustion',
    'syngas-combustion',
    'coalgas-combustion',
    'hydrogen-combustion',
    'coalslurry-combustion',
    'tholin-to-glycerol'
]
for r in recipe:
    if recipe[r]['category'] == 'handcrafting':
        recipe_exclusion_list.append(r)
    if recipe[r]['category'] == 'converter-valve':
        recipe_exclusion_list.append(r)
for r in recipe_exclusion_list:
    del recipe[r]


resource_exclusion_list = [
#    'nexelit-rock'
]
for r in resource_exclusion_list:
    del resource[r]


ass_exclusion_list = [
    'crash-site-assembling-machine-1-repaired',
    'crash-site-assembling-machine-2-repaired'
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

dimensions_dict = {}
for m in ass_list:
    box = raw['assembling-machine'][m['name']]['selection_box']
    dim = (box[1][0] - box[0][0], box[1][1] - box[0][1])
    dimensions_dict[m['name']] = dim
for m in mining_list:
    box = raw['mining-drill'][m['name']]['selection_box']
    dim = (box[1][0] - box[0][0], box[1][1] - box[0][1])
    dimensions_dict[m['name']] = dim
for m in furnace_list:
    box = raw['furnace'][m['name']]['selection_box']
    dim = (box[1][0] - box[0][0], box[1][1] - box[0][1])
    dimensions_dict[m['name']] = dim
for m in raw['rocket-silo'].values():
    box = raw['rocket-silo'][m['name']]['selection_box']
    dim = (box[1][0] - box[0][0], box[1][1] - box[0][1])
    dimensions_dict[m['name']] = dim

area_dict = {m:(dimensions_dict[m][0] * dimensions_dict[m][1]) for m in dimensions_dict}
            

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
    if 'assembling-machine-2' in choices:
        category_choice[c] = 'assembling-machine-2'
category_choice['smelting'] = 'electric-furnace'
category_choice['basic-solid'] = 'electric-mining-drill'
category_choice['cooling'] = 'cooling-tower-mk02'


category_speed = {c:speed_dict[category_choice[c]] for c in category_dict}
category_area = {c:area_dict[category_choice[c]] for c in category_dict}



# Adding modules

#speed_bonus_category = {}
prod_list = [r for r in raw['module']['productivity-module-3']['limitation'] if r not in recipe_exclusion_list]
prod_list = []
for r in prod_list:
    r_with_prod = copy.deepcopy(recipe[r])
    slots = slot_dict[category_choice[r_with_prod['category']]]
    prod_bonus = slots * 0.1
    #speed_bonus = max(1 - slots * 0.15, 0.2)
    r_with_prod['name'] += '(prod)'
    for mat in r_with_prod['products']:
        mat['amount'] *= 1 + prod_bonus
    recipe[r_with_prod['name']] = r_with_prod


from cvxopt import matrix, spmatrix
from cvxopt import solvers

# Constructing recipe sparse matrix

x = []
I = []
J = []
recipe_list = list(recipe.values())

resource = {}
resource_list = list(resource.values())


N = len(item) + len(fluid) 
#M = len(recipe) + len(prod_list) + len(resource)
M = len(recipe) + len(resource)


for r in range(0, len(recipe_list)):
    net_flux = {}
    for mat in recipe_list[r]['ingredients']:
        if mat['name'] not in net_flux:
            net_flux[mat['name']] = -((mat['probability'] if ('probability' in mat) else 1) * mat['amount'])
        else:
            net_flux[mat['name']] -= (mat['probability'] if ('probability' in mat) else 1) * mat['amount']
    for mat in recipe_list[r]['products']:
        if mat['name'] not in net_flux:
            net_flux[mat['name']] = +((mat['probability'] if ('probability' in mat) else 1) * mat['amount'])
        else:
            net_flux[mat['name']] += (mat['probability'] if ('probability' in mat) else 1) * mat['amount']
    for name in net_flux:
        x.append(net_flux[name] / recipe_list[r]['energy'])
        I.append(index_mat[name])
        J.append(r)

"""
for r in range(0, len(prod_list)):
    net_flux = {}
    for mat in recipe[prod_list[r]]['ingredients']:
        if mat['name'] not in net_flux:
            net_flux[mat['name']] = -((mat['probability'] if ('probability' in mat) else 1) * mat['amount'])
        else:
            net_flux[mat['name']] -= (mat['probability'] if ('probability' in mat) else 1) * mat['amount']
    for mat in recipe[prod_list[r]]['products']:
        if mat['name'] not in net_flux:
            net_flux[mat['name']] = +((mat['probability'] if ('probability' in mat) else 1) * mat['amount']) * 1.4
        else:
            net_flux[mat['name']] += (mat['probability'] if ('probability' in mat) else 1) * mat['amount'] * 1.4
    for name in net_flux:
        x.append(net_flux[name] / recipe_list[r]['energy'])
        I.append(index_mat[name])
        J.append(r + len(recipe_list))
"""
        
for r in range(0, len(resource_list)):
    for mat in resource_list[r]['mineable_properties']['products']:
        x.append((mat['probability'] if ('probability' in mat) else 1) * mat['amount'])
        I.append(index_mat[mat['name']])
        #J.append(r + len(recipe_list) + len(prod_list))
        J.append(r + len(recipe_list))



# Add zero-cost sources and sinks

"""
# Input for iron-plate
source = [
    'mukmoux-fat',
    'salt',
    'titanium-plate',
    'zinc-plate',
    'copper-plate',
    'coal',
    'coke',
    'nickel-plate',
    'tin-plate',
    'lead-plate',
    'niobium-plate',
    'glass',
    'borax',
    'chromium',
    'oil-sand',
    'sulfur',
    'nichrome',
    'iron-ore',
    'crude-oil',
    'phosphate-rock',
    'nexelit-plate',
    'stone',
    'log',
    'steam',
    'active-carbon'
]
sink = [
    'hydrogen'
]
"""
"""
# Input for nitrogen
source = [
#    'filtration-media'
]
sink = [
]
"""
"""
# Input for copper-plate
source = [
    'copper-ore',
    'salt',
    'borax',
    'nexelit-plate',
    'coal',
    'coke',
#    'crude-oil',
    'log',
#    'tar',
    'stone',
    'active-carbon',
    'glass',
    'nichrome',
    'mukmoux-fat',
    'iron-plate',
    'sulfur',
    'steel-plate',
    'titanium-plate',
    'lead-plate',
    'chromium',
    'nickel-plate',
#    'organics',
    'log',
    'filtration-media'
]
sink = [
#    'gravel',
#    'stone',
#    'ash'
]
"""
"""
# Input for fuel cell mk05
source = [
    'lead-plate',
    'uranium-ore',
    'biofilm',
    'filtration-media',
    'steel-plate',
    'salt',
    'iron-plate',
    'borax',
    'iron-plate',
    'titanium-plate',
    'copper-plate',
    'iron-ore'
]
sink = []
"""

"""
# Input for science
source = [
    'aluminium-plate',
    'chromium',
    'coal',
    'copper-plate',
    'iron-plate',
    'lead-plate',
    'nexelit-plate',
    'nickel-plate',
    'phosphate-rock',
    'salt',
    'tin-plate',    
    'titanium-plate',
    'uranium-ore',
    'zinc-plate',

    'crude-oil',
    'tar',
    'oil-sand',
    'raw-coal',
    'rare-earth-ore',
    'sulfur',
    'raw-borax',
    'niobium-ore',
    'molybdenum-ore',
    'ore-quartz',
    'regolite-rock',
    'kimberlite-rock',
    'stone',

    'nichrome'
]
sink = []
"""
"""
# Input for science (ore)
source = [
    'ore-aluminium',
    'raw-borax',
    'ore-chromium',
    'raw-coal',
    'copper-ore',
    'crude-oil',
    'iron-ore',
    'ore-lead',
    'molybdenum-ore',
    'ore-nickel',
    'niobium-ore',
    'oil-sand',
    'ore-quartz',
    'ore-tin',
    'ore-titanium',
    'ore-zinc',
    'phosphate-rock',
    'rare-earth-ore',
    'regolite-rock',
    'salt',
    'sulfur',
    'tar',
    'uranium-ore',
    'kimberlite-rock',
#    'coal',
    'nexelit-ore',
    'stone',
    
    'log'
]
sink = []
"""

"""
# Input for nickel/chromium/nichrome
source = [
    'ore-nickel',
    'ore-chromium',
    'borax',
    'salt',
    'sulfur',
    'active-carbon',
#    'tar',
#    'crude-oil',
    'nexelit-plate',
    'mukmoux-fat',
    'log',
    'coke',
    'coal',
    'tin-plate',
    'iron-plate',
    'steel-plate',
    'copper-plate',
    'titanium-plate',
    'zinc-plate',
    'phosphate-rock',
    'lead-plate',
    'graphite',
    'filtration-media',
    'glass'
]
sink = [
    'crushed-quartz',
    'tailings-dust',
    'nexelit-ore',
    'hydrogen'
]
"""

"""
# Input for electronic-circuit
source = [
    'iron-plate',
    'copper-plate',
    'titanium-plate',
    'tin-plate',
    'chromium',
    'nickel-plate',
    'nexelit-plate',
    'aluminium-plate',
    'coal',
    'coke',
    'lead-plate',
    'zinc-plate',
    'salt',
    'crude-oil',
    'tar',
    'glass',
    'nichrome',
    'mukmoux-fat',
    'active-carbon'
]
sink = []
"""
"""
# Input for steel
source = [
#    'molten-iron',
#    'borax',
#    'coal'
]
sink = [
]
"""
"""
# Input for zinc-plate/agzn-alloy/silver-plate/lead-plate
source = [
    'ore-zinc',
    'ore-lead',
    'borax',
    'nichrome',
    'chromium',
    'raw-coal',
    'coal',
    'coke',
    'phosphate-rock',
    'copper-plate',
    'tin-plate',
    'iron-plate',
    'steel-plate',
    'sodium-hydroxide',
    'glass',
    'filtration-media',
    'active-carbon',
    'titanium-plate',
    'nexelit-plate',
    'crude-oil',
#    'tar',
    'salt',
    'limestone',
    'log',
    'sulfur'
]
sink = []
"""

source = [
    'crude-oil',
#    'tar',
    'log'
]
sink = []

for i in range(0, len(source)):
    x.append(1)
    I.append(index_mat[source[i]])
    #J.append(i + len(recipe_list) + len(prod_list) + len(resource_list))
    J.append(i + len(recipe_list) + len(resource_list))
    
for i in range(0, len(sink)):
    x.append(-1)
    I.append(index_mat[sink[i]])
    #J.append(i + len(recipe_list) + len(prod_list) + len(resource_list) + len(source))
    J.append(i + len(recipe_list) + len(resource_list) + len(source))

M += len(source) + len(sink)


# Specifying linear programming cost

#c = matrix(1, (M, 1), 'd')

"""
c = matrix([category_area[m['category']]/category_speed[m['category']] for m in recipe_list] +
           [category_area[recipe[m]['category']]/category_speed[recipe[m]['category']] for m in prod_list] +
           [category_area[m['resource_category']]/category_speed[m['resource_category']] for m in resource_list] +
           [0] * (len(source) + len(sink)),
           (M, 1), 'd')
"""


c = matrix([1/category_speed[m['category']] for m in recipe_list] +
#           [1/category_speed[recipe[m]['category']] for m in prod_list] +
           [1/category_speed[m['resource_category']] for m in resource_list] +
           [0] * (len(source) + len(sink)),
           (M, 1), 'd')

           

G = spmatrix([1] * M, [i for i in range(0, M)], [i for i in range(0, M)], (M, M), 'd')
h = matrix(0, (M, 1), 'd')

A = spmatrix(x, I, J, (N, M), 'd')
b = matrix(0, (N, 1), 'd')
#b[index_mat['automation-science-pack']] = 1
#b[index_mat['logistic-science-pack']] = 1
#b[index_mat['chemical-science-pack']] = 1
#b[index_mat['production-science-pack']] = 1
#b[index_mat['utility-science-pack']] = 1
#b[index_mat['space-science-pack']] = 1

b[index_mat['combustion-mixture1']] = 1380


#b[index_mat['nitrogen']] = 175
#b[index_mat['iron-plate']] = 120
#b[index_mat['filtration-media']] = 0.6176

#b[index_mat['copper-plate']] = 60
#b[index_mat['aromatics']] = 100
#b[index_mat['molten-nexelit']] = 30 * 5
#b[index_mat['nexelit-plate']] = 30

#b[index_mat['yellow-cake']] = 1


#b[index_mat['chromium']] = 40
#b[index_mat['nickel-plate']] = 30
#b[index_mat['nichrome']] = 10

#b[index_mat['log']] = 60 / 5

#b[index_mat['steel-plate']] = 15
#b[index_mat['zinc-plate']] = 60
#b[index_mat['agzn-alloy']] = 8
#b[index_mat['silver-plate']] = 25
#b[index_mat['lead-plate']] = 42
#b[index_mat['tin-plate']] = 40

#opts = {'maxiters' : 1000, 'abstol' : 1e-12, 'reltol' : 1e-12, 'feastol' : 1e-12}
opts = {'maxiters' : 1000, 'abstol' : 1e-9, 'reltol' : 1e-6, 'feastol' : 1e-7}
sol = solvers.lp(c, -G, -h, A, b, options=opts)



print(c.trans() * sol['x'])
z = list(zip(list(sol['x']), [r['name'] for r in recipe_list + resource_list]))
z.sort()
z.reverse()



def print_mat_info(sol, mat_name):
    threshold = 1e-6
    
    producer = []
    for i in range(0, len(recipe_list)):
        if sol['x'][i] < threshold:
            continue
        for mat in recipe_list[i]['products']:
            if mat['name'] == mat_name:
                producer.append((i, ((mat['probability'] if ('probability' in mat) else 1) * mat['amount']) * sol['x'][i]))
    producer.sort(key=lambda p: -p[1])
    producer = [p[0] for p in producer]
                
    consumer = []
    for i in range(0, len(recipe_list)):
        if sol['x'][i] < threshold:
            continue
        for mat in recipe_list[i]['ingredients']:
            if mat['name'] == mat_name:
                consumer.append((i, ((mat['probability'] if ('probability' in mat) else 1) * mat['amount']) * sol['x'][i]))
    consumer.sort(key=lambda c: -c[1])
    consumer = [c[0] for c in consumer]

    print("PRODUCERS FOR {}".format(mat_name))
    for i in producer:
        print("{:<25} {:<5} {:<20} {:<20} {:<5} ({} {})".format(recipe_list[i]['name'], i, recipe_list[i]['category'], sol['x'][i], recipe_list[i]['energy'], category_choice[recipe_list[i]['category']], sol['x'][i]/category_speed[recipe_list[i]['category']]))
        print("    ingredients:")
        for p in recipe_list[i]['ingredients']:
            print("        {}".format(p))
        print("    products:")
        for p in recipe_list[i]['products']:
            print("        {}".format(p))
    print()
    
    print("CONSUMERS FOR {}".format(mat_name))
    for i in consumer:
        #print("{:<25} {:<5} {:<20} {:<20} {:<5}".format(recipe_list[i]['name'], i, recipe_list[i]['category'], sol['x'][i], recipe_list[i]['energy']))
        print("{:<25} {:<5} {:<20} {:<20} {:<5} ({} {})".format(recipe_list[i]['name'], i, recipe_list[i]['category'], sol['x'][i], recipe_list[i]['energy'], category_choice[recipe_list[i]['category']], sol['x'][i]/category_speed[recipe_list[i]['category']]))
        print("    ingredients:")
        for p in recipe_list[i]['ingredients']:
            print("        {}".format(p))
        print("    products:")
        for p in recipe_list[i]['products']:
            print("        {}".format(p))

    print()




def print_dominant_recipes(sol, n:int):
    print()
    for i in range(0, n):
        print("{:f} {:<25} {:<25} ({:<25} {:f})".format(*z[i], recipe[z[i][1]]['category'], category_choice[recipe[z[i][1]]['category']], z[i][0] / category_speed[recipe[z[i][1]]['category']]))



def total_area(sol):
    return sum([category_area[recipe_list[i]['category']] * sol['x'][i] / category_speed[recipe_list[i]['category']] for i in range(0, len(recipe_list))])

from math import ceil

def total_machines(sol):
    return sum([(0 if (sol['x'][i] / category_speed[recipe_list[i]['category']] < 1e-6) else ceil(sol['x'][i] / category_speed[recipe_list[i]['category']])) for i in range(0, len(recipe_list))])

source_info = list(zip(source, list(sol['x'][-len(source)-len(sink):])))
sink_info = list(zip(sink, list(sol['x'][-len(sink):])))
resource_info = [(resource_list[i]['name'], sol['x'][i + len(recipe)]) for i in range(0, len(resource_list))]

def total_throughput(sol, mat_name:str):
    throughput = 0
    for i in range(0, len(recipe_list)):
        for out in recipe_list[i]['products']:
            if out['name'] == mat_name:
                throughput += out['amount'] / recipe_list[i]['energy'] * sol['x'][i]
    return throughput
    


metals = [mat for mat in item if ('alloy' in mat or 'plate' in mat)]
metals_throughput = []
for mat in metals:
    throughput = 0
    for i in range(0, len(recipe_list)):
        for out in recipe_list[i]['products']:
            if out['name'] == mat:
                throughput += out['amount'] / recipe_list[i]['energy'] * sol['x'][i]
    metals_throughput.append((mat, throughput))


"""
unlocked_recipes = []
for t in raw['technology'].values():
    effs = t.get('effects')
    if effs:
        for e in effs:
            if e['type'] == 'unlock-recipe':
                unlocked_recipes.append(e['recipe'])
"""

"""
for r in recipe_list:
    if r['category'] == 'pa':
        print(r['name'])
"""

