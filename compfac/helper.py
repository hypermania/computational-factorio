import bp

def print_recipe(recipe):
    print(recipe['name'])
    print("time usage: {}".format(recipe['energy']))
    print('ingredients:')
    for mat in recipe['ingredients']:
        print('    {} {}'.format(mat['name'], mat['amount']))
    print('products:')
    for mat in recipe['products']:
        print('    {} {}'.format(mat['name'], +((mat['probability'] if ('probability' in mat) else 1) * (mat.get('amount') if (mat.get('amount') != None) else (0.5 * (mat.get('amount_min') + mat.get('amount_max'))))) ))


empty_warehouse_str = '0eNqFj8sKwjAURP9l1hFMqX3kV0Sk1YsG2puYhxpK/t2mbty5nGHmMLNgnCJZpzlALdAXwx7quMDrGw9T8UKyBAUdaIYAD3NRNu1eg6O7iZ52jh6RfCCHLKD5Sm8omU8CxEEHTV/iJtKZ4zyuSSX/sQSs8WvdcFmxIqu+E0hQdSVzoW+L1M8BgSc5vxWqTtZt3bdNK/fNocn5A/uFTko='

warehouse = bp.decode('0eNqFkMEOgjAQRP9lzjWhDQL2V4whqKs2Qou0VQnpv9uCGm8ed3f2zexO2Lee+kFpBzlBHYy2kNsJVp1106aeG3uChHLUgUE3Xar6cfVoBroYb2k10M2TdTQgMCh9pCckDzsG0k45RQtxLsZa+24flZL/YzH0xsZ1o1OKiBSbimGEzAWPPm9hfVJtVC8WH+8v2raNP1/ifIF310xE7sH4dK4IuxRyPkz+/IHhHoGzr6h4Xuabsih5VqyLEF616Ga6')

def set_warehouse(directive):
    result_warehouses = []

    directive_items = list(directive.items())
    for i in range(0, len(directive_items)):
        if i % 30 == 0:
            index = 1
            result_warehouse = bp.decode(empty_warehouse_str)
            result_warehouse['blueprint']['entities'][0]['request_filters'] = []
            filters = result_warehouse['blueprint']['entities'][0]['request_filters']
            result_warehouses.append(result_warehouse)
        filters.append({'index': index,
                        'name': directive_items[i][0],
                        'count': directive_items[i][1]})
        index += 1

    return result_warehouses
        
            
        
"""    
    index = 1
    for name, val in directive.items():
        filters.append({'index': index,
                        'name': name,
                        'count': val})
        index += 1

    return result_warehouses
        
"""
