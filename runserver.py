import os
import logging
import json
import argparse
from flask import Flask, request, redirect, url_for, abort, \
     render_template, flash, make_response
from pgoapi import PGoApi
from geopy.geocoders import GoogleV3
from time import sleep
from inventory2csv import get_csv, get_json, get_keys

def get_pos_by_name(location_name):
    geolocator = GoogleV3()
    loc = geolocator.geocode(location_name)
    log.info('Your given location: %s', loc.address.encode('utf-8'))
    log.info('lat/long/alt: %s %s %s', loc.latitude, loc.longitude, loc.altitude)
    return (loc.latitude, loc.longitude, loc.altitude)
    # If you are having problems with the above three lines; that means your API isn't configured or it expired or something happened related to api. If that is the case, just manually input the coordinates of you current location. Don't make it something too ridiculous, or it might result in a soft ban. For example, you would replace the above three lines with something like: return (33.0, 112.0, 0.0)

def init_config():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", help="Debug Mode", action='store_true')
    config = parser.parse_args()

    return config

app = Flask(__name__)
log = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(module)10s] [%(levelname)5s] %(message)s')
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("pgoapi").setLevel(logging.INFO)
logging.getLogger("rpc_api").setLevel(logging.INFO)

config = init_config()

if config.debug:
  logging.getLogger("requests").setLevel(logging.INFO)
  logging.getLogger("pgoapi").setLevel(logging.INFO)
  logging.getLogger("rpc_api").setLevel(logging.INFO)

pokemon_names = json.load(open("name_id.json"))
api = PGoApi(config.__dict__, pokemon_names)

def request_user_info(req):
  auth_service = req.form['auth_service']
  username = req.form['username']
  password = req.form['password']
  location = req.form['location']
  position = get_pos_by_name(location)
  api.set_position(*position)

  if not api.login(auth_service, username, password, False):
    return {}

  res = {}

  while 'GET_INVENTORY' not in res.get('responses', {}):
    res = api.heartbeat()
    sleep(2)

  return res['responses']

@app.route("/")
def home():
  return render_template('index.html')

@app.route("/csv", methods=['POST'])
def csv():
  user_info = request_user_info(request)
  csv = get_csv(user_info)

  response = make_response(csv)
  response.headers["Content-Disposition"] = "attachment; filename=pokemonIVs.csv"
  return response

@app.route("/data_table", methods=['POST'])
def data_table():
  user_info = request_user_info(request)
  data = get_json(user_info)

  keys = get_keys()
  return render_template('data_table.html', data=data, keys=keys)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
