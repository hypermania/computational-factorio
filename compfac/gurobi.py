import json
import io
import copy
from slpp import slpp as lua
import numpy as np

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

recipe_exclusion_list = [ # disabled recipes
    'crushing-iron',
    'crushing-copper',
    'dedicated-syngas-from-hydrogen-1',
    'raw-borax',
    'hotair-nexelit-plate'
] + [ # locked recipes
    'sinter-iron-2',
    'sinter-iron-1',
    'sinter-chromium',
    'sinter-zinc-2',
    'sinter-zinc-1',
    'tholin-to-glycerol'
] + [ # recipes I don't want for this calculation
]


combustion_recipes = set()
for r in recipe.values():
    for mat in r['products']:
        if mat['name'] == 'combustion-mixture1':
            if mat.get('temperature') == None:
                combustion_recipes.add(r['name'])
                continue
            if mat['temperature'] < 900:
                combustion_recipes.add(r['name'])
            
recipe_exclusion_list += list(combustion_recipes)



for r in recipe:
    if recipe[r]['category'] == 'handcrafting':
        recipe_exclusion_list.append(r)
    if recipe[r]['category'] == 'converter-valve':
        recipe_exclusion_list.append(r)
for r in recipe_exclusion_list:
    del recipe[r]


resource_exclusion_list = [
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
category_choice['fawogae'] = 'fawogae-plantation'

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
source = [
    'raw-coal',
    'water'
]
sink = []

# Set output
output = {
    'coal': 30,
    'coke': 30,
    'graphite': 15 * (2/5) * 2
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
#m.setObjective(sum(M_vec), GRB.MINIMIZE)
m.setObjective(sum([area_vec[i] * M_vec[i] for i in range(0, len(recipe_list))]), GRB.MINIMIZE)

# Set machine-recipe constraints
for i in range(0, len(recipe_list)):
    crafting_speed = category_speed[recipe_list[i]['category']]
    m.addConstr(crafting_speed * M_vec[i] >= R_vec[i])

# Set material constraints

# Recipe constraints
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

# Fuel consumption
chemical_fuel_choice = 'coal'
fuel_value = item[chemical_fuel_choice]['fuel_value']
for r in range(0, len(recipe_list)):
    machine_name = category_choice[recipe_list[r]['category']]
    if machine_name in ass:
        machine_raw = raw['assembling-machine'][machine_name]
        energy_usage = ass[machine_name]['energy_usage']
        effectivity = ass[machine_name].get('burner_effectivity')
    elif machine_name in furnace:
        machine_raw = raw['furnace'][machine_name]
        energy_usage = furnace[machine_name]['energy_usage']
        effectivity = furnace[machine_name].get('burner_effectivity')
    else:
        continue

    if machine_raw['energy_source']['type'] == 'burner':
        crafting_speed = category_speed[recipe_list[r]['category']]
        fuel_consumption_rate = energy_usage / (fuel_value * effectivity)
        mat_constr_expr[index_mat[chemical_fuel_choice]] -= fuel_consumption_rate * (R_vec[r] / crafting_speed)
        
        
# Output constraints
for name in output:
    mat_constr_expr[index_mat[name]] -= output[name]
for i in range(0, len(source)):
    mat_constr_expr[index_mat[source[i]]] += I_vec[i]

    

# Compilation of constraints
for expr in mat_constr_expr:
    m.addConstr(expr == 0)

m.Params.PoolSolutions = 10
m.Params.PoolSearchMode = 2
m.Params.timeLimit = 1.5 * 3600.0
m.optimize()

"""
machine_count = {}
for v in M_vec:
    if v.x > 0:
        r = v.varName[:-9]
        cat = category_choice[recipe[v.varName[:-9]]['category']]
        print('%s %g %s %g' % (v.varName, v.x, cat, m.getVarByName(r).x))
        if cat not in machine_count:
            machine_count[cat] = v.x
        else:
            machine_count[cat] += v.x

for v in I_vec:
    if v.x > 0:
        print('%s %g' % (v.varName, v.x))
"""


m.Params.SolutionNumber = 0
machine_count = {}
for v in M_vec:
    if v.getAttr(GRB.Attr.Xn) > 0:
        r = v.varName[:-9]
        cat = category_choice[recipe[v.varName[:-9]]['category']]
        print('%s %g %s %g' % (v.varName,
                               v.getAttr(GRB.Attr.Xn),
                               cat,
                               m.getVarByName(r).getAttr(GRB.Attr.Xn)))
        if cat not in machine_count:
            machine_count[cat] = v.getAttr(GRB.Attr.Xn)
        else:
            machine_count[cat] += v.getAttr(GRB.Attr.Xn)

for v in I_vec:
    if v.getAttr(GRB.Attr.Xn) > 0:
        print('%s %g' % (v.varName, v.getAttr(GRB.Attr.Xn)))

        
print('Obj: %g' % m.objVal)

    


def print_mat_info(mat_name):
    
    producer = []
    for i in range(0, len(recipe_list)):
        if M_vec[i].getAttr(GRB.Attr.Xn) == 0:
            continue
        for mat in recipe_list[i]['products']:
            if mat['name'] == mat_name:
                producer.append((i, ((mat['probability'] if ('probability' in mat) else 1) * mat['amount']) * R_vec[i].getAttr(GRB.Attr.Xn) / recipe_list[i]['energy']))
    producer.sort(key=lambda p: -p[1])
    producer = [p[0] for p in producer]
                
    consumer = []
    for i in range(0, len(recipe_list)):
        if M_vec[i].getAttr(GRB.Attr.Xn) == 0:
            continue
        for mat in recipe_list[i]['ingredients']:
            if mat['name'] == mat_name:
                consumer.append((i, ((mat['probability'] if ('probability' in mat) else 1) * mat['amount']) * R_vec[i].getAttr(GRB.Attr.Xn) / recipe_list[i]['energy']))
                #consumer.append((i, ((mat['probability'] if ('probability' in mat) else 1) * mat['amount']) * sol['x'][i]))
    consumer.sort(key=lambda c: -c[1])
    consumer = [c[0] for c in consumer]

    print("PRODUCERS FOR {}".format(mat_name))
    for i in producer:
        print("{:<25} {:<5} {:<20} {:<20} {:<5} ({} {})".format(recipe_list[i]['name'], i, recipe_list[i]['category'], R_vec[i].getAttr(GRB.Attr.Xn), recipe_list[i]['energy'], category_choice[recipe_list[i]['category']], M_vec[i].getAttr(GRB.Attr.Xn)))
        print("    ingredients:")
        for p in recipe_list[i]['ingredients']:
            print("        {}".format(p))
        print("    products:")
        for p in recipe_list[i]['products']:
            print("        {}".format(p))
    print()
    
    print("CONSUMERS FOR {}".format(mat_name))
    for i in consumer:
        print("{:<25} {:<5} {:<20} {:<20} {:<5} ({} {})".format(recipe_list[i]['name'], i, recipe_list[i]['category'], R_vec[i].getAttr(GRB.Attr.Xn), recipe_list[i]['energy'], category_choice[recipe_list[i]['category']], M_vec[i].getAttr(GRB.Attr.Xn)))
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
    return sum([category_area[recipe_list[i]['category']] * M_vec[i].getAttr(GRB.Attr.Xn) for i in range(0, len(recipe_list)) if M_vec[i].getAttr(GRB.Attr.Xn) > 0])

""" 
source_info = list(zip(source, list(sol['x'][-len(source)-len(sink):])))
sink_info = list(zip(sink, list(sol['x'][-len(sink):])))
resource_info = [(resource_list[i]['name'], sol['x'][i + len(recipe)]) for i in range(0, len(resource_list))]
"""

"""
def total_throughput(sol, mat_name:str):
    throughput = 0
    for i in range(0, len(recipe_list)):
        for out in recipe_list[i]['products']:
            if out['name'] == mat_name:
                throughput += out['amount'] / recipe_list[i]['energy'] * sol['x'][i]
    return throughput
    
"""

m.Params.SolutionNumber = 0
# Prepare data-lookup for control system information
#used_recipes = [v.varName for v in R_vec if v.x > 0]
#used_sources = [v.varName for v in I_vec if v.x > 0]

#used_recipes = [v.varName for v in R_vec if v.getAttr(GRB.Attr.Xn) > 0]
used_recipes = set([v.varName for v in R_vec if v.getAttr(GRB.Attr.Xn) > 0])
#used_recipes.remove('supercritical-combustion')
used_recipes = list(used_recipes)
used_sources = [v.varName for v in I_vec if v.getAttr(GRB.Attr.Xn) > 0]
used_output = ['combustion-mixture1(output)']
    
ingredient_dict = {}
product_dict = {}
used_materials_set = set()
for r in used_recipes:
    ingredient_dict[r] = set()
    product_dict[r] = set()
    for mat in recipe[r]['ingredients']:
        ingredient_dict[r].add(mat['name'])
        used_materials_set.add(mat['name'])
    for mat in recipe[r]['products']:
        product_dict[r].add(mat['name'])
        used_materials_set.add(mat['name'])
    
for r in used_sources:
    ingredient_dict[r] = set()
    product_dict[r] = set([r[:-8]])
for r in used_output:
    ingredient_dict[r] = set([r[:-8]])
    product_dict[r] = set()
    used_materials_set.add(r[:-8])

nodes = used_recipes + used_sources + used_output
producer_dict = {}
consumer_dict = {}
for mat in used_materials_set:
    producer_dict[mat] = set()
    consumer_dict[mat] = set()
for node in nodes:
    for mat in ingredient_dict[node]:
        consumer_dict[mat].add(node)
    for mat in product_dict[node]:
        producer_dict[mat].add(node)

# Compute the dimension of the nullspace
used_materials_list = list(used_materials_set)
used_materials_index = {used_materials_list[i]:i for i in range(0, len(used_materials_list))}
A = []
for r in used_recipes:
    net_flux = {}
    for mat in recipe[r]['ingredients']:
        if mat['name'] not in net_flux:
            net_flux[mat['name']] = -((mat['probability'] if ('probability' in mat) else 1) * mat['amount'])
        else:
            net_flux[mat['name']] -= (mat['probability'] if ('probability' in mat) else 1) * mat['amount']
    for mat in recipe[r]['products']:
        if mat['name'] not in net_flux:
            net_flux[mat['name']] = +((mat['probability'] if ('probability' in mat) else 1) * mat['amount'])
        else:
            net_flux[mat['name']] += (mat['probability'] if ('probability' in mat) else 1) * mat['amount']
    row = [(net_flux[used_materials_list[i]] if (used_materials_list[i] in net_flux) else 0) for i in range(0, len(used_materials_list))]
    A.append(row)

    
for r in range(0, len(used_recipes)):
    machine_name = category_choice[recipe[used_recipes[r]]['category']]
    if machine_name in ass:
        machine_raw = raw['assembling-machine'][machine_name]
        energy_usage = ass[machine_name]['energy_usage']
        effectivity = ass[machine_name].get('burner_effectivity')
    elif machine_name in furnace:
        machine_raw = raw['furnace'][machine_name]
        energy_usage = furnace[machine_name]['energy_usage']
        effectivity = furnace[machine_name].get('burner_effectivity')
    else:
        continue

    if machine_raw['energy_source']['type'] == 'burner':
        #print(used_recipes[r], energy_usage, effectivity)
        crafting_speed = category_speed[recipe[used_recipes[r]]['category']]
        fuel_consumption_rate = energy_usage / (fuel_value * effectivity)
        A[r][used_materials_index[chemical_fuel_choice]] -= fuel_consumption_rate / crafting_speed


for mat in used_sources:
    index = used_materials_index[mat[:-8]]
    row = [0] * len(used_materials_list)
    row[index] = 1
    A.append(row)
for mat in used_output:
    index = used_materials_index[mat[:-8]]
    row = [0] * len(used_materials_list)
    row[index] = -1
    A.append(row)
    
A = np.array(A).transpose()
nullspace_dim = A.shape[1] - np.linalg.matrix_rank(A)




# Greedy reduction of nullspace
from itertools import combinations
from functools import reduce


used_materials = list(used_materials_set)
result = {nodes[i]:i for i in range(0, len(nodes))}
controls = []
last_groups = len(result) + 1
while last_groups > len(set(result.values())):
    if len(set(result.values())) == 3:
        break
    last_groups = len(set(result.values()))

    found_new_control = False

    for rank in range(0, len(used_materials)):
        print("rank = {}".format(rank))
        mat_combinations = list(combinations(used_materials, rank))
        for comb in mat_combinations:
            mat_groups = reduce(lambda accum, mat: accum | {result[r] for r in producer_dict[mat]} | {result[r] for r in consumer_dict[mat]}, comb, set())
            if len(mat_groups) == rank + 1:
                it = list(mat_groups)
                control_item = []
                for mat in comb:
                    control_item.append(mat)
                for group_index in it:
                    control_item.append([r for r in nodes if result[r] == group_index])
                controls.append(control_item)
                fix = it[0]
                for node in nodes:
                    if result[node] in it:
                        result[node] = fix
                for mat in comb:
                    used_materials.remove(mat)
                found_new_control = True
            if found_new_control:
                break
        if found_new_control:
            break
    if found_new_control:
        continue



controls_dict = {}
for c in controls:
    if len(c) == 3:
        controls_dict[c[0]] = c
    if len(c) == 5:
        controls_dict[c[0]] = c
        controls_dict[c[1]] = c

        
def control_vecs(c):
    n = len(c) // 2 # number of materials
    mats = [c[i] for i in range(0, n)] # material names
    groups = [c[i] for i in range(n, len(c))]
    excess = [np.array([0.0] * n) for i in range(0, len(groups))]
    involved = []
    for g in range(0, len(groups)):
        g_involved = set()
        for r in range(0, len(groups[g])):
            r_name = groups[g][r]
            for l in range(0, n):
                mat = mats[l]
                if r_name in producer_dict[mat]:
                    for p in recipe[r_name]['products']:
                        if p['name'] == mat:
                            excess[g][l] += m.getVarByName(r_name).x * p['amount'] * (p['probability'] if ('probability' in p) else 1) / recipe[r_name]['energy']
                    g_involved.add(r_name)
                if r_name in consumer_dict[mat]:
                    for p in recipe[r_name]['ingredients']:
                        if p['name'] == mat:
                            excess[g][l] -= m.getVarByName(r_name).x * p['amount'] * (p['probability'] if ('probability' in p) else 1) / recipe[r_name]['energy']
                    g_involved.add(r_name)
        involved.append(g_involved)

    return excess, involved
            
    
    
        
def control_1_var(mat, group1, group2):
    excess1 = 0
    for r in group1:
        if r in producer_dict[mat]:
            for p in recipe[r]['products']:
                if p['name'] == mat:
                    excess1 += m.getVarByName(r).x * p['amount'] * (p['probability'] if ('probability' in p) else 1) / recipe[r]['energy']
        if r in consumer_dict[mat]:
            for p in recipe[r]['ingredients']:
                if p['name'] == mat:
                    excess1 -= m.getVarByName(r).x * p['amount'] * (p['probability'] if ('probability' in p) else 1) / recipe[r]['energy']
        
    excess2 = 0
    for r in group2:
        if r in producer_dict[mat]:
            for p in recipe[r]['products']:
                if p['name'] == mat:
                    excess2 += m.getVarByName(r).x * p['amount'] * (p['probability'] if ('probability' in p) else 1) / recipe[r]['energy']
        if r in consumer_dict[mat]:
            for p in recipe[r]['ingredients']:
                if p['name'] == mat:
                    excess2 -= m.getVarByName(r).x * p['amount'] * (p['probability'] if ('probability' in p) else 1) / recipe[r]['energy']
        
    return excess1, excess2

def control_2_var(mat1, mat2, group1, group2, group3):
    excess1 = np.array([0, 0], dtype=np.float64)
    for r in group1:
        if r in producer_dict[mat1]:
            for p in recipe[r]['products']:
                if p['name'] == mat1:
                    excess1[0] += m.getVarByName(r).x * p['amount'] * (p['probability'] if ('probability' in p) else 1) / recipe[r]['energy']
        if r in consumer_dict[mat1]:
            for p in recipe[r]['ingredients']:
                if p['name'] == mat1:
                    excess1[0] -= m.getVarByName(r).x * p['amount'] * (p['probability'] if ('probability' in p) else 1) / recipe[r]['energy']
        if r in producer_dict[mat2]:
            for p in recipe[r]['products']:
                if p['name'] == mat2:
                    excess1[1] += m.getVarByName(r).x * p['amount'] * (p['probability'] if ('probability' in p) else 1) / recipe[r]['energy']
        if r in consumer_dict[mat2]:
            for p in recipe[r]['ingredients']:
                if p['name'] == mat2:
                    excess1[1] -= m.getVarByName(r).x * p['amount'] * (p['probability'] if ('probability' in p) else 1) / recipe[r]['energy']
        
    excess2 = np.array([0, 0], dtype=np.float64)
    for r in group2:
        if r in producer_dict[mat1]:
            for p in recipe[r]['products']:
                if p['name'] == mat1:
                    excess2[0] += m.getVarByName(r).x * p['amount'] * (p['probability'] if ('probability' in p) else 1) / recipe[r]['energy']
        if r in consumer_dict[mat1]:
            for p in recipe[r]['ingredients']:
                if p['name'] == mat1:
                    excess2[0] -= m.getVarByName(r).x * p['amount'] * (p['probability'] if ('probability' in p) else 1) / recipe[r]['energy']
        if r in producer_dict[mat2]:
            for p in recipe[r]['products']:
                if p['name'] == mat2:
                    excess2[1] += m.getVarByName(r).x * p['amount'] * (p['probability'] if ('probability' in p) else 1) / recipe[r]['energy']
        if r in consumer_dict[mat2]:
            for p in recipe[r]['ingredients']:
                if p['name'] == mat2:
                    excess2[1] -= m.getVarByName(r).x * p['amount'] * (p['probability'] if ('probability' in p) else 1) / recipe[r]['energy']
        
    excess3 = np.array([0, 0], dtype=np.float64)
    for r in group3:
        if r in producer_dict[mat1]:
            for p in recipe[r]['products']:
                if p['name'] == mat1:
                    excess3[0] += m.getVarByName(r).x * p['amount'] * (p['probability'] if ('probability' in p) else 1) / recipe[r]['energy']
        if r in consumer_dict[mat1]:
            for p in recipe[r]['ingredients']:
                if p['name'] == mat1:
                    excess3[0] -= m.getVarByName(r).x * p['amount'] * (p['probability'] if ('probability' in p) else 1) / recipe[r]['energy']
        if r in producer_dict[mat2]:
            for p in recipe[r]['products']:
                if p['name'] == mat2:
                    excess3[1] += m.getVarByName(r).x * p['amount'] * (p['probability'] if ('probability' in p) else 1) / recipe[r]['energy']
        if r in consumer_dict[mat2]:
            for p in recipe[r]['ingredients']:
                if p['name'] == mat2:
                    excess3[1] -= m.getVarByName(r).x * p['amount'] * (p['probability'] if ('probability' in p) else 1) / recipe[r]['energy']
        
    return excess1, excess2, excess3




for i in range(0, len(controls)):
    c = controls[i]
    if len(c) == 3:
        group_a = set(c[1]) & (producer_dict[c[0]] | consumer_dict[c[0]])
        group_b = set(c[2]) & (producer_dict[c[0]] | consumer_dict[c[0]])
        throughput = (0.0, 0.0)
        try:
            throughput = control_1_var(*c)
        except:
            throughput = (0.0, 0.0)
        print("{}: {}\n{}, {}\n{}, {}\n".format(i, c[0], group_a, group_b, *throughput))
    else:
        print("{}: {}\n".format(i, c))



"""
max_util_recipes = []
for r in used_recipes:
    if abs(m.getVarByName(r).x - category_speed[recipe[r]['category']] * m.getVarByName(r + '(machine)').x) < 1e-2:
        max_util_recipes.append(r)
"""




