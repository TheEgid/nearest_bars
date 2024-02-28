import os
import argparse
import platform
import json
import requests
import logging
import folium
from flask import Flask
from geopy import distance
from environs import Env
from services import storage_json_io_decorator

TEMP_FILE = 'temporary_data.json'


def get_coordinates(_address, locationiq_org_token):
    url = f'https://locationiq.org/v1/search.php?'
    params = {
        'q': _address,
        'format': 'json',
        'limit': 1,
        'key': locationiq_org_token,
        'accept_language': 'RU',
        'countrycodes': ['RU'],
    }
    response = requests.get(url=url, params=params)
    response.raise_for_status()
    address = response.json()[0]
    if not address:
        return None
    return float(address['lat']), float(address['lon'])


def get_distance_km(start_address, finish_address, token):
    if isinstance(finish_address, str):
        finish_address = get_coordinates(finish_address, token)
    return distance.distance(start_address, finish_address).km


def get_bar_info(bar_data, start_address, token):
    bar_info = {}
    coordinates = list(bar_data['geoData']['coordinates'])
    coordinates.reverse()
    latidude, longtidude = coordinates
    bar_info['latidude'] = latidude
    bar_info['longtidude'] = longtidude
    bar_info['name'] = bar_data['Name']
    bar_info['distance'] = get_distance_km(start_address, coordinates, token)
    bar_info['address'] = bar_data['Address']
    logging.info(f"{bar_info['name']} - {bar_info['distance']}")
    return bar_info


def get_nearest_bars(bars, amount_of_bars=5):
    bars.sort(key=lambda dictionary: dictionary['distance'], reverse=False)
    return bars[:amount_of_bars]


@storage_json_io_decorator(storage_file_pathname=TEMP_FILE)
def get_all_bars_with_distance(bars, my_address, token):
    return [get_bar_info(bar_data, my_address, token) for bar_data in bars]


def add_marker(location, out_map, text, icon):
    if isinstance(location, tuple):
        folium.Marker(list(location), popup=text, tooltip=text, icon=icon). \
            add_to(out_map)


def transfer_html(temp_html_filepath='index.html'):
    with open(temp_html_filepath, encoding='utf-8') as html_file:
        return html_file.read()


def start_flask_server(func, host, port, rule='/'):
    activate_job = Flask(__name__)
    activate_job.add_url_rule(rule, '', func)
    activate_job.run(host, port, debug=True)


def save_html_bars_map(bars, my_address, temp_html_filepath='index.html'):
    my_location_marker = f'You are here!'
    zoom_param = 14
    out_map = folium.Map(location=my_address, zoom_start=zoom_param)
    icon = folium.Icon(color='red', icon='info-sign')
    add_marker(location=my_address, out_map=out_map, text=my_location_marker, icon=icon)
    for bar_info in bars:
        coords = bar_info['latidude'], bar_info['longtidude']
        bar_info_marker = f"{bar_info['name']} - {bar_info['address']}"
        icon = folium.Icon(color='green', icon='cloud')
        add_marker(location=coords, out_map=out_map, text=bar_info_marker, icon=icon)
    out_map.save(outfile=temp_html_filepath)


def draw_nearest_bars_map(location_address, bars, token):
    location_coordinates = get_coordinates(location_address, token)
    all_bars = get_all_bars_with_distance(bars, location_coordinates, token)
    nearest_bars = get_nearest_bars(all_bars)
    save_html_bars_map(bars=nearest_bars, my_address=location_coordinates)


def get_args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('my_address', type=str, nargs='+',
                        help='My location address')
    parser.add_argument('-t', '--test', action='store_true', default=False,
                        help='Test mode')
    return parser


def main():
    env = Env()
    env.read_env()
    logging.basicConfig(level=logging.ERROR)
    args = get_args_parser().parse_args()
    token = env.str("API_TOKEN")

    if args.test:
        logging.info(' Test mode: temp data from json file')
    else:
        logging.info(' Normal mode: delete temp files')
        if os.path.exists(TEMP_FILE):
            os.remove(TEMP_FILE)

    my_address = ' '.join(args.my_address)
    # logging.info(f'location: {my_address}, coords: {get_coordinates(my_address, token)}')
    with open('bars_db.json', 'r', encoding='utf-8') as fl:
        bars_data = json.load(fl)

    draw_nearest_bars_map(location_address=my_address, bars=bars_data, token=token)

    host, port = 'localhost', 8001
    if platform.system() != "Windows":
        host, port = '0.0.0.0', 80
    start_flask_server(func=transfer_html, host=host, port=port)


if __name__ == '__main__':
    main()
