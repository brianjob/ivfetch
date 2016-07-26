import json

SPECIES     = 'Species'
NICKNAME    = 'Nickname'
MOVE_1      = 'Move 1'
MOVE_2      = 'Move 2'
FAST_DPS    = 'Fast DPS'
SPECIAL_DPS = 'Special DPS'
MAX_DPS     = 'Max DPS'
EFF_HP     = 'Effective HP'
MAX_DMG     = 'Max Damage'
COMBO_DMG   = 'Combo Damage'
HEIGHT      = 'Height'
WEIGHT      = 'Weight'
HP          = 'HP'
MAX_HP      = 'Max HP'
ATTACK      = 'ATTACK'
DEFENSE     = 'DEFENSE'
STAMINA     = 'STAMINA'
CP          = 'CP'
IV          = 'IV %'


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

def get_keys():
  return [SPECIES, NICKNAME, MOVE_1, MOVE_2, FAST_DPS, SPECIAL_DPS, MAX_DPS, EFF_HP,
  MAX_DMG, COMBO_DMG, HEIGHT, WEIGHT, HP, MAX_HP, ATTACK, DEFENSE, STAMINA, CP, IV]


def get_json(data):
  inventory_items = data.get('GET_INVENTORY', {}).get('inventory_delta', {}).get('inventory_items', [])
  inventory_items_dict_list = map(lambda x: x.get('inventory_item_data', {}), inventory_items)
  inventory_items_pokemon_list = filter(lambda x: 'pokemon_data' in x and 'is_egg' not in x['pokemon_data'],
    inventory_items_dict_list)
  inventory_items_pokemon_list = map(lambda x: x['pokemon_data'], inventory_items_pokemon_list)

  print 'found {} pokemon'.format(len(inventory_items_pokemon_list))

  rows = []

  for pokemon in inventory_items_pokemon_list:
    row = {}
    species = get_type(pokemon['pokemon_id'])
    move_1 = get_move(pokemon['move_1'])
    move_2 = get_move(pokemon['move_2'])
    dps_obj = get_dps_obj(species, move_1, move_2)

    row[SPECIES] = species
    row[NICKNAME] = unicode(pokemon.get('nickname', ''))
    row[MOVE_1] = move_1
    row[MOVE_2] = move_2
    row[FAST_DPS] = dps_obj.get('Fast DPS', '')
    row[SPECIAL_DPS] = dps_obj.get('Special DPS', '')
    row[MAX_DPS] = dps_obj.get('Max DPS', '')
    row[EFF_HP] = dps_obj.get('Eff. HP', '')
    row[MAX_DMG] = dps_obj.get('Max Damage', '')
    row[COMBO_DMG] = dps_obj.get('F&S Combo Dmg', '')
    row[HEIGHT] = '{0:.2f}'.format(pokemon['height_m'])
    row[WEIGHT] = '{0:.2f}'.format(pokemon['weight_kg'])
    row[HP] = pokemon.get('stamina', 0)
    row[MAX_HP] = pokemon['stamina_max']
    row[ATTACK] = pokemon.get('individual_attack', 0)
    row[DEFENSE] = pokemon.get('individual_defense', 0)
    row[STAMINA] = pokemon.get('individual_stamina', 0)
    row[CP] = pokemon['cp']
    row[IV] = '{0:.2f}'.format(pokemonIVPercentage(pokemon))

    rows.append(row)

  return rows


def get_csv(data):
  rows = get_json(data)
  keys = get_keys()

  table = [keys] + map(lambda x: [x[key] for key in keys], rows)

  csv_str = "\n".join([','.join(map(unicode, x)) for x in table])

  return csv_str
