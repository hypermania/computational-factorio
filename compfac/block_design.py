import json
import io
from slpp import slpp as lua

recipe = open("recipe-lister/recipe.json", "r")
recipe_obj = json.load(recipe)

item = open("recipe-lister/item.json", "r")
item_obj = json.load(item)

fluid = open("recipe-lister/fluid.json", "r")
fluid_obj = json.load(fluid)

generator = open("recipe-lister/generator.json", "r")
generator_obj = json.load(generator)

raw = open("py_data.lua", "r")
raw_str = raw.read()
raw_obj = lua.decode(raw_str)

#raw_obj['recipe']['wpu']

from jsonpath_ng import jsonpath
from jsonpath_ng.ext import parse
#jsonpath_exp = parse('$..selection_box')
#jsonpath_exp = parse('$.assembling-machine.*.name')
#jsonpath_exp = parse('$.recipe.*.name')
#jsonpath_exp = parse('$..*[?(@name="automated-factory-mk01")]')
jsonpath_exp = parse('$.*.*[?name="log1"]')
match = jsonpath_exp.find(raw_obj)
print(len(match))
if match:
    print(str(match[0].full_path))
#if match:
#    print(str(match[0].full_path))
#for i in range(600, 610):
#    print(str(match[i].full_path), match[i].value)

for key, item in raw_obj.items():
    print(key, len(item))

raw_recipes = list(raw_obj['recipe'].items())
diff_set = []
for name in recipe_obj:
    if name not in raw_obj['recipe']:
        diff_set.append(name)

#raw_obj['electric-pole']

for name in raw_obj['recipe']:
    if raw_obj['recipe'][name].get('category') not in raw_obj['recipe-category']:
        print(name)
        break
