import base64
import zlib
import json
import xml


def decode(bp_str:str):
    text_skip = bp_str[1:]
    decoded = base64.b64decode(text_skip)
    decompressed = zlib.decompress(decoded)
    bp = json.loads(decompressed)

    return bp

def encode(bp_obj:dict):
    json_str = json.dumps(bp_obj)
    compressed = zlib.compress(bytes(json_str, encoding='utf-8'))
    encoded = base64.b64encode(compressed)
    text = '0' + str(encoded, encoding='utf-8')

    return text

def load_blueprint(filename:str):
    f = open(filename, 'r', encoding='utf-8')
    bp = decode(f.read())
    f.close()
    
    return bp
    
def save_blueprint(bp:dict, filename:str):
    f = open(filename, 'w', encoding='utf-8')
    f.write(encode(bp))
    f.close()

def set_name(bp:dict, name:str):
    bp['blueprint']['label'] = name

def get_entities(bp:dict, name:str):
    entities = []
    for entity in bp['blueprint']['entities']:
        if entity['name'] == name:
            entities.append(entity)
    return entities


def find_entity_by_coord(blueprint, x, y):
    for ent in blueprint['blueprint']['entities']:
        if ent['position']['x'] == x and ent['position']['y'] == y:
            return ent
    return None
