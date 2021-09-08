import csv
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

tsv_file = open("../../localised-names/entity.tsv")
read_tsv = csv.reader(tsv_file, delimiter="\t")

entity_name_map = {}
for row in read_tsv:
    entity_name_map[row[0]] = row[1]
