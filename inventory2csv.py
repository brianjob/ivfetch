import json

with open('lookups/moves.json') as moves_file:
  moves = json.load(moves_file)

with open('lookups/pokemon.json') as pokemon_file:
  pokemon_types = json.load(pokemon_file)

with open('lookups/dps_chart.json') as dps_file:
  dps = json.load(dps_file)


def pokemonIVPercentage(pokemon):
  return ((pokemon.get('individual_attack', 0) + pokemon.get('individual_stamina', 0) + pokemon.get(
    'individual_defense', 0) + 0.0) / 45.0) * 100.0


def get_move(move_id):
  results = filter(lambda x: x.get('id', -1) == move_id, moves)
  if len(results) > 0:
    return results[0]['name']
  else:
    return move_id


def get_type(type_id):
  results = filter(lambda x: int(x.get('Number', '-1')) == int(type_id), pokemon_types)
  if (len(results) > 0):
    return results[0]['Name']
  else:
    return type_id

def get_dps_obj(pokemon_name, move_1, move_2):
  results = filter(lambda x: x['Name'] == pokemon_name and x['Fast'] == move_1 and x['Spacial'] == move_2, dps)

  if (len(results) > 0):
    return results[0]
  else:
    return {}

def get_csv(data):
  inventory_items = data['GET_INVENTORY'].get('inventory_delta', {}).get('inventory_items', [])
  inventory_items_dict_list = map(lambda x: x.get('inventory_item_data', {}), inventory_items)
  inventory_items_pokemon_list = filter(lambda x: 'pokemon_data' in x and 'is_egg' not in x['pokemon_data'],
    inventory_items_dict_list)
  inventory_items_pokemon_list = map(lambda x: x['pokemon_data'], inventory_items_pokemon_list)

  print 'found {} pokemon'.format(len(inventory_items_pokemon_list))

  rows = []

  keys = ['Species', 'Nickname', 'Move 1', 'Move 2',
  'Fast DPS', 'Special DPS', 'Max DPS', 'Effective HP', 'Max Damage', 'Combo Damage',
  'Height', 'Weight', 'HP', 'Max HP', 'Attack', 'Defense', 'Stamina', 'CP', 'IV %']
  
  rows.append(keys)

  for pokemon in inventory_items_pokemon_list:
    row = {}
    species = get_type(pokemon['pokemon_id'])
    move_1 = get_move(pokemon['move_1'])
    move_2 = get_move(pokemon['move_2'])
    dps_obj = get_dps_obj(species, move_1, move_2)

    row['Species'] = species
    row['Nickname'] = pokemon.get('nickname', '').encode('utf8')
    row['Move 1'] = move_1
    row['Move 2'] = move_2
    row['Fast DPS'] = dps_obj.get('Fast DPS', '')
    row['Special DPS'] = dps_obj.get('Special DPS', '')
    row['Max DPS'] = dps_obj.get('Max DPS', '')
    row['Effective HP'] = dps_obj.get('Eff. HP')
    row['Max Damage'] = dps_obj.get('Max Damage')
    row['Combo Damage'] = dps_obj.get('F&S Combo Dmg', '')
    row['Height'] = str(pokemon['height_m'])
    row['Weight'] = str(pokemon['weight_kg'])
    row['HP'] = pokemon['stamina']
    row['Max HP'] = pokemon['stamina_max']
    row['Attack'] = pokemon.get('individual_attack', 0)
    row['Defense'] = pokemon.get('individual_defense', 0)
    row['Stamina'] = pokemon.get('individual_stamina', 0)
    row['CP'] = pokemon['cp']
    row['IV %'] = pokemonIVPercentage(pokemon)

    rows.append([row[key] for key in keys])

  val = "\n".join([','.join(map(str, x)) for x in rows])

  return val
