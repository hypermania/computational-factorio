"""
GRecipe class
-------------
A "generalized recipe" is a collection of recipes with proportional recipe speeds,
so that it has a fixed vector of inputs and outputs,
and fixing any one of the input/output variables fixes the recipe speed of the entire collection.
-------------
Expected functionalities:

1. store involved recipes and recipe speeds
2. store material constraints
3. manage input/output
4. compute control systems for each involved material
-------------
Thoughts:
1. it may be easier to make "generalized" recipe to mean a collection of recipes with >1 nullspace dimension

"""
class GRecipe():
    def __init__(self):
        recipe_names = []
        mat_constraints = []
        

class GFRecipeOptimizer():
    def __init__(self, mod:Mod):
        mod = mod
        return
    def __init__(self):
        mod = mod.default_mod
        return
    
def produce_mod_info():
    mod_info = None
    return mod_info

mod = produce_mod_info()
tin_block = GFRecipeOptimizer(mod_info)

# think about how to specify machines

class ModInfo():
    def __init__(self, directory):
        info = load_mod(directory)
    def set_default(self):
        global default_mod
        default_mod = self

tin_block.recipe_class('')
tin_block.add_recipe('tin-plate-tier-4', machine='smelter', module='speed-2')
tin_block.add_local_source('tin-rock')
tin_block.add_external_source('coal', limit=30)
tin_block.add_external_sink('ash')
tin_block.add_area_constraint(6000)
tin_block.maxmize_objective('tin-plate')
