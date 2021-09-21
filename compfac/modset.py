import json
import copy
from slpp import slpp as lua

class ModSet():
    def __init__(self, dat_directory=None,
                 item_exclusion_list=[],
                 fluid_exclusion_list=[],
                 recipe_exclusion_list=[],
                 recipe_category_exclusion_list=[],
                 resource_exclusion_list=[],
                 ass_exclusion_list=[]): 

        # Load from directory
        self.item = json.load(open(dat_directory + "/item.json", "r"))
        self.fluid = json.load(open(dat_directory + "/fluid.json", "r"))
        self.recipe = json.load(open(dat_directory + "/recipe.json", "r"))
        self.resource = json.load(open(dat_directory + "/resource.json", "r"))
        self.ass = json.load(open(dat_directory + "/assembling-machine.json", "r"))
        self.mining = json.load(open(dat_directory + "/mining-drill.json", "r"))
        self.furnace = json.load(open(dat_directory + "/furnace.json", "r"))

        self.raw = lua.decode(open(dat_directory + "/raw.lua", "r").read())

        # Exclude unwanted stuff
        for mat in item_exclusion_list:
            if mat in self.item:
                del self.item[mat]

        for mat in fluid_exclusion_list:
            if mat in self.fluid:
                del self.fluid[mat]

        recipe_exclusion_list_2 = []
        for r in recipe.values():
            if r['category'] in recipe_category_exclusion_list:
                recipe_exclusion_list_2.append(r['name'])
        for r in recipe_exclusion_list:
            if r in self.recipe:
                del self.recipe[mat]
        for r in recipe_exclusion_list_2:
            if r in self.recipe:
                del self.recipe[mat]

        for r in resource_exclusion_list:
            if r in self.resource:
                del self.resource[r]

        for m in ass_exclusion_list:
            if m in self.ass:
                del self.ass[m]


