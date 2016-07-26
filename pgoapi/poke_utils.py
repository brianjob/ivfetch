import os
import csv

def pokemonIVPercentage(pokemon):
    return ((pokemon.get('individual_attack', 0) + pokemon.get('individual_stamina', 0) + pokemon.get(
        'individual_defense', 0) + 0.0) / 45.0) * 100.0


def get_inventory_list(res):
    inventory_delta = res['responses']['GET_INVENTORY'].get('inventory_delta', {})
    inventory_items = inventory_delta.get('inventory_items', [])
    inventory_items_dict_list = map(lambda x: x.get('inventory_item_data', {}), inventory_items)
    inventory_items_pokemon_list = filter(lambda x: 'pokemon_data' in x and 'is_egg' not in x['pokemon_data'],
                                          inventory_items_dict_list)

    return inventory_items_pokemon_list


def get_inventory_data(res, pokenames):
    inventory_items_pokemon_list = get_inventory_list(res)

    return (os.linesep.join(map(lambda x: "{0}, CP {1}, IV {2:.2f}".format(
        pokenames[str(x['pokemon_data']['pokemon_id'])].encode('ascii', 'ignore'),
        x['pokemon_data']['cp'],
        pokemonIVPercentage(x['pokemon_data'])), inventory_items_pokemon_list)))


def write_inventory_to_csv(res, filename):
    inventory_items_pokemon_list = get_inventory_list(res)

    if len(inventory_items_pokemon_list) < 1:
        return False

    with open(filename, 'wb') as csvfile:
        w = csv.writer(csvfile, dialect='excel')
        keys = inventory_items_pokemon_list[0]['pokemon_data'].keys()
        w.writerow(keys)
        for pokemon in inventory_items_pokemon_list:
            w.writerow([pokemon['pokemon_data'].get(key, '') for key in keys])
