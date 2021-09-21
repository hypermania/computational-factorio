from math import ceil
from helper import print_recipe
from preprocess import item, fluid, recipe, resource, ass, furnace, raw, dimensions_dict, box_dict, slot_dict, collision_dict, normalized_box_dict, center_dict

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



# Calculates chemical fuel consumption
chemical_fuel_choice = 'raw-coal'
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


# Calculates liquid fuel consumption
