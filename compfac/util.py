from functools import reduce

from preprocess import item, fluid, recipe, resource, ass, furnace, raw, dimensions_dict, box_dict, slot_dict, collision_dict, normalized_box_dict, center_dict
from helper import print_recipe

# Helper functions

# Gives the average net flux per craft
def average_net_flux_per_craft(recipe):
    net_flux = {}
    for mat in recipe['ingredients']:
        flux_per_craft = -((mat['probability'] if ('probability' in mat) else 1) * mat['amount'])
        if mat['name'] not in net_flux and flux_per_craft != 0:
            net_flux[mat['name']] = 0
        if mat['name'] in net_flux:
            net_flux[mat['name']] += flux_per_craft
    for mat in recipe['products']:
        flux_per_craft = +((mat['probability'] if ('probability' in mat) else 1) * (mat.get('amount') if (mat.get('amount') != None) else (0.5 * (mat.get('amount_min') + mat.get('amount_max')))))
        if mat['name'] not in net_flux and flux_per_craft != 0:
            net_flux[mat['name']] = 0
        if mat['name'] in net_flux:
            net_flux[mat['name']] += flux_per_craft

    return net_flux

# Gives the average net flux per unit time at unit crafting speed
def average_net_flux(recipe):
    net_flux = average_net_flux_per_craft(recipe)
    for mat in net_flux:
        net_flux[mat] /= recipe['energy']
    return net_flux

# Gives rate of fuel consumption
def fuel_consumption(machine, fuel_name):
    energy_usage = machine['energy_usage']
    return 


# Finds recipes with a certain ingredient
def find_consumer_list(mat):
    result = []
    for r in recipe.values():
        if mat in [item['name'] for item in r['ingredients']]:
            result.append(r['name'])
    return result


def find_consumer(mat):
    for r in find_consumer_list(mat):
        print(r)

            
# Finds recipes with a certain product
def find_producer_list(mat):
    result = []
    for r in recipe.values():
        if mat in [item['name'] for item in r['products']]:
            result.append(r['name'])
    return result


def find_producer(mat):
    for r in find_producer_list(mat):
        print(r)


# Give ingredients/products of a given recipe
def ingredients(r):
    return list(map(lambda mat: mat['name'], r['ingredients']))


def products(r):
    return list(map(lambda mat: mat['name'], r['products']))

"""
has_molten = lambda mat: 'molten' in mat
molten_mat = list(filter(has_molten, fluid.keys()))
molten_steel_succ = list(reduce(lambda x, y: x | set(products(recipe[y])), find_consumer_list('molten-steel'), set()))
"""

fuel_categories = list(raw['fuel-category'].keys())

class Context():
    def __init__(self):
        self.good = 2

class Game():
    def __init__(self, context=None):
        self.context = context


