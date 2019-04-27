import json
import os
import logging
from flask import Flask
import folium
import argparse
from yandex_geocoder import Client
from geopy import distance
from services import storage_json_io_decorator


def get_coordinates(_address):
    latitude, longitude = Client.coordinates(_address)
    return float(longitude), float(latitude)


def get_distance_km(start_address, finish_address):
    if isinstance(finish_address, str):
        finish_address = get_coordinates(finish_address)
    return distance.distance(start_address, finish_address).km


def get_bar_info(bar_data, start_address):
    bar_info = {}
    coordinates = list(bar_data['geoData']['coordinates'])
    coordinates.reverse()
    latidude, longtidude = coordinates
    bar_info['latidude'] = latidude
    bar_info['longtidude'] = longtidude
    bar_info['name'] = bar_data['Name']
    bar_info['distance'] = get_distance_km(start_address, coordinates)
    bar_info['address'] = bar_data['Address']
    logging.info(' {} - {}'.format(bar_info['name'], bar_info['distance']))
    return bar_info


def get_nearest_bars(bars, amount_of_bars=5):
    bars.sort(key=lambda dictionary: dictionary['distance'], reverse=False)
    return bars[:amount_of_bars]


@storage_json_io_decorator(storage_file_pathname='temporary_data.json')
def get_all_bars_with_distance(bars, my_address):
    return [get_bar_info(bar_data, my_address) for bar_data in bars]


def add_marker(location, out_map, text):
    if isinstance(location, tuple):
        location = list(location)
        folium.Marker(location, popup=text, tooltip=text).add_to(out_map)


def transfer_html(temp_html_filepath='index.html'):
    with open(temp_html_filepath, encoding='utf-8') as html_file:
        return html_file.read()


def start_flask_server(func, ip, rule='/'):
    activate_job = Flask(__name__)
    activate_job.add_url_rule(rule, '', func)
    activate_job.run(ip, debug=False)


def save_html_bars_map(bars, my_address, temp_html_filepath='index.html'):
    my_location_marker = 'You are here'
    zoom_param = 14
    out_map = folium.Map(location=my_address, zoom_start=zoom_param)
    add_marker(location=my_address, out_map=out_map, text=my_location_marker)
    for bar_info in bars:
        coords = bar_info['latidude'], bar_info['longtidude']
        bar_info_marker = '{} {}'.format(bar_info['name'], bar_info['address'])
        add_marker(location=coords, out_map=out_map, text=bar_info_marker)
    out_map.save(outfile=temp_html_filepath)


def draw_nearest_bars_map(location_address, bars):
    location_coordinates = get_coordinates(location_address)
    all_bars = get_all_bars_with_distance(bars, location_coordinates)
    nearest_bars = get_nearest_bars(all_bars)
    save_html_bars_map(bars=nearest_bars, my_address=location_coordinates)


def get_args_parser():
    formatter_class = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(formatter_class=formatter_class)
    parser.add_argument('my_address', type=str, nargs='+',
                        help='My location address')
    parser.add_argument('-t', '--test', action='store_true', default=False,
                        help='Test mode')
    return parser


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    temp_file = 'temporary_data.json'
    args = get_args_parser().parse_args()

    if args.test:
        logging.info(' Test mode: temp data from json file')
    else:
        logging.info(' Normal mode: delete temp files')
        if os.path.exists(temp_file):
            os.remove(temp_file)

    my_address = ' '.join(args.my_address)
    logging.info(' My location: {}'.format(my_address))

    with open('bars_db.json', 'r') as fl:
        bars_data = json.load(fl)

    draw_nearest_bars_map(location_address=my_address, bars=bars_data)
    start_flask_server(func=transfer_html, ip='127.0.0.1')
