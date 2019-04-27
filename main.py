import json
import pprint
import logging
from yandex_geocoder import Client
from geopy import distance


def get_coordinates(_address):
    latitude, longitude = Client.coordinates(_address)
    return float(longitude), float(latitude)


def get_distance_km(start_address, finish_address):
    start_address = get_coordinates(start_address)
    if isinstance(finish_address, str):
        finish_address = get_coordinates(finish_address)
    return distance.distance(start_address, finish_address).km


def get_bar_with_distance(bar, start_address):
    bar_with_distance = {}
    coordinates = list(bar['geoData']['coordinates'])
    coordinates.reverse()
    latidude, longtidude = coordinates
    bar_with_distance['latidude'] = latidude
    bar_with_distance['longtidude'] = longtidude
    bar_with_distance['title'] = bar['Name']
    bar_with_distance['distance'] = get_distance_km(start_address, coordinates)
    bar_with_distance['district'] = bar['District']
    logging.info(' {} - {}'.format(bar_with_distance['title'], bar_with_distance['distance']))
    return bar_with_distance


def get_nearest_bars(bars, amount_of_bars=5):
    bars.sort(key=lambda dictionary: dictionary['distance'], reverse=False)
    return bars[:amount_of_bars]


def storage_json_io(storage_file_pathname):
    def memoize(func):
        def decorate(*args, **kwargs):
            try:
                with open(storage_file_pathname, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                return data
            except (FileNotFoundError, IOError):
                data = func(*args, **kwargs)
                with open(storage_file_pathname, 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False)
                return data
        return decorate
    return memoize


@storage_json_io(storage_file_pathname='temporary_data.json')
def get_all_bars_with_distance(bars, my_address):
    return [get_bar_with_distance(bar, my_address) for bar in bars]


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    my_address = 'Красная площадь'
    with open('bars_db.json', 'r') as file:
        bars = json.load(file)

    bars_with_distance = get_all_bars_with_distance(bars, my_address)
    pprint.pprint(get_nearest_bars(bars_with_distance))



