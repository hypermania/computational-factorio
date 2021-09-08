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
    'dedicated-syngas-from-hydrogen-1'
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


import gurobipy as gp
from gurobipy import GRB


# Defining the problem

# Add recipes and resources
recipe_list = list(recipe.values())
resource = {}
resource_list = list(resource.values())

# Add zero-cost sources and sinks
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
    'sulfur',
    'steam',
    'stone'
]
sink = []

# Set output
output = {
    "zinc-plate":60
}

N = len(item) + len(fluid) 
M = len(recipe) + len(resource)

# Create model
m = gp.Model("BlockDesign")

# Add variables
R_vec = []
M_vec = []
I_vec = []
for r in recipe_list:
    R_vec.append(m.addVar(name=r['name']))
for r in recipe_list:
    M_vec.append(m.addVar(vtype=GRB.INTEGER, name=r['name']+"(machine)"))
for name in source:
    I_vec.append(m.addVar(name=name+"(source)"))

# Set objective (Minimize machine number)
area_vec = [category_area[r['category']] for r in recipe_list]
m.setObjective(sum(M_vec), GRB.MINIMIZE)
#m.setObjective(sum([area_vec[i] * M_vec[i] for i in range(0, len(recipe_list))]), GRB.MINIMIZE)

# Set machine-recipe constraints
for i in range(0, len(recipe_list)):
    crafting_speed = category_speed[recipe_list[i]['category']]
    m.addConstr(crafting_speed * M_vec[i] >= R_vec[i])

# Set material constraints
mat_constr_expr = [gp.LinExpr() for i in range(0, N)]
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
        mat_constr_expr[index_mat[name]] += (net_flux[name] / recipe_list[r]['energy']) * R_vec[r]
        
for name in output:
    mat_constr_expr[index_mat[name]] -= output[name]
for i in range(0, len(source)):
    mat_constr_expr[index_mat[source[i]]] += I_vec[i]

for expr in mat_constr_expr:
    m.addConstr(expr == 0)

m.addConstr(I_vec[0] <= 50)
    
m.optimize()

for v in M_vec:
    if v.x > 0:
        print('%s %g %s' % (v.varName, v.x, category_choice[recipe[v.varName[:-9]]['category']]))

for v in I_vec:
    if v.x > 0:
        print('%s %g' % (v.varName, v.x))

print('Obj: %g' % m.objVal)

    

# Specifying linear programming cost

"""
c = matrix([category_area[m['category']]/category_speed[m['category']] for m in recipe_list] +
           [category_area[recipe[m]['category']]/category_speed[recipe[m]['category']] for m in prod_list] +
           [category_area[m['resource_category']]/category_speed[m['resource_category']] for m in resource_list] +
           [0] * (len(source) + len(sink)),
           (M, 1), 'd')
"""

"""
c = matrix([1/category_speed[m['category']] for m in recipe_list] +
           [1/category_speed[m['resource_category']] for m in resource_list] +
           [0] * (len(source) + len(sink)),
           (M, 1), 'd')


#b[index_mat['automation-science-pack']] = 1
#b[index_mat['logistic-science-pack']] = 1
#b[index_mat['chemical-science-pack']] = 1
#b[index_mat['production-science-pack']] = 1
#b[index_mat['utility-science-pack']] = 1
#b[index_mat['space-science-pack']] = 1

#b[index_mat['steel-plate']] = 15
b[index_mat['zinc-plate']] = 60
#b[index_mat['agzn-alloy']] = 8
#b[index_mat['silver-plate']] = 25
#b[index_mat['lead-plate']] = 42

opts = {'maxiters' : 1000, 'abstol' : 1e-9, 'reltol' : 1e-6, 'feastol' : 1e-7}
sol = solvers.lp(c, -G, -h, A, b, options=opts)
"""


"""
print(c.trans() * sol['x'])
z = list(zip(list(sol['x']), [r['name'] for r in recipe_list + resource_list]))
z.sort()
z.reverse()
"""


def print_mat_info(mat_name):
    
    producer = []
    for i in range(0, len(recipe_list)):
        if M_vec[i].x == 0:
            continue
        for mat in recipe_list[i]['products']:
            if mat['name'] == mat_name:
                producer.append((i, ((mat['probability'] if ('probability' in mat) else 1) * mat['amount']) * R_vec[i].x / recipe_list[i]['energy']))
    producer.sort(key=lambda p: -p[1])
    producer = [p[0] for p in producer]
                
    consumer = []
    for i in range(0, len(recipe_list)):
        if M_vec[i].x == 0:
            continue
        for mat in recipe_list[i]['ingredients']:
            if mat['name'] == mat_name:
                consumer.append((i, ((mat['probability'] if ('probability' in mat) else 1) * mat['amount']) * R_vec[i].x / recipe_list[i]['energy']))
                #consumer.append((i, ((mat['probability'] if ('probability' in mat) else 1) * mat['amount']) * sol['x'][i]))
    consumer.sort(key=lambda c: -c[1])
    consumer = [c[0] for c in consumer]

    print("PRODUCERS FOR {}".format(mat_name))
    for i in producer:
        print("{:<25} {:<5} {:<20} {:<20} {:<5} ({} {})".format(recipe_list[i]['name'], i, recipe_list[i]['category'], R_vec[i].x, recipe_list[i]['energy'], category_choice[recipe_list[i]['category']], M_vec[i].x))
        print("    ingredients:")
        for p in recipe_list[i]['ingredients']:
            print("        {}".format(p))
        print("    products:")
        for p in recipe_list[i]['products']:
            print("        {}".format(p))
    print()
    
    print("CONSUMERS FOR {}".format(mat_name))
    for i in consumer:
        print("{:<25} {:<5} {:<20} {:<20} {:<5} ({} {})".format(recipe_list[i]['name'], i, recipe_list[i]['category'], R_vec[i].x, recipe_list[i]['energy'], category_choice[recipe_list[i]['category']], M_vec[i].x))
        print("    ingredients:")
        for p in recipe_list[i]['ingredients']:
            print("        {}".format(p))
        print("    products:")
        for p in recipe_list[i]['products']:
            print("        {}".format(p))

    print()



"""
def print_dominant_recipes(sol, n:int):
    print()
    for i in range(0, n):
        print("{:f} {:<25} {:<25} ({:<25} {:f})".format(*z[i], recipe[z[i][1]]['category'], category_choice[recipe[z[i][1]]['category']], z[i][0] / category_speed[recipe[z[i][1]]['category']]))
"""



def total_area():
    return sum([category_area[recipe_list[i]['category']] * M_vec[i].x for i in range(0, len(recipe_list)) if M_vec[i].x > 0])

""" 
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
    
"""

#for v in M_vec:
#    if v.x > 0:
#        print('%s %g %s' % (v.varName, v.x, category_choice[recipe[v.varName[:-9]]['category']]))


def span(recipe_name):
    if recipe_name not in recipe:
        print("Error")
        return
    used_recipes = [v.varName[:-9] for v in M_vec if v.x > 0]
    result = set()
    visited = set()
    return []
