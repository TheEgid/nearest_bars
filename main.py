from __future__ import annotations

import argparse
import json
import logging
import os
import platform
import time
from functools import cache
from pathlib import Path

import folium  # type: ignore
import requests
from environs import Env
from flask import Flask, request
from geopy import distance
from requests.exceptions import RequestException

TEMP_FILE = Path("temporary_data.json")
BARS_DB_FILE = Path("bars_db.json")


# Production WSGI app

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health():
    return "OK", 200


@app.route("/", methods=["GET"])
def index_route():
    address = request.args.get("address", "Москва Тучковская улица 9")
    token = os.environ.get("API_TOKEN")
    if not token:
        return "API_TOKEN not configured", 500
    try:
        with open(BARS_DB_FILE, encoding="utf-8") as fl:
            bars_data = json.load(fl)
    except Exception as e:
        logging.error("Bars data load error: %s", e)
        return "Bars data unavailable", 500
    draw_nearest_bars_map(location_address=address, bars_data=bars_data, token=token)
    html = transfer_html()
    return html


@cache
def get_coordinates(address: str, token: str) -> tuple[float, float] | None:
    url = "https://locationiq.org/v1/search.php"
    params = {
        "q": address,
        "format": "json",
        "limit": 1,
        "key": token,
        "accept_language": "RU",
        "countrycodes": "RU",
    }
    retries = 2
    backoff = 1
    for attempt in range(retries + 1):
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if not data:
                return None
            return float(data[0]["lat"]), float(data[0]["lon"])
        except (RequestException, ValueError, KeyError, IndexError) as e:
            logging.error("Coordinate fetch failed (attempt %d/%d): %s", attempt + 1, retries + 1, e)
            if attempt == retries:
                return None
            time.sleep(backoff)
            backoff *= 2


def get_distance_km(start: tuple[float, float], finish: tuple[float, float]) -> float:
    return distance.distance(start, finish).km


def get_bar_info(bar_data: dict, start_coords: tuple[float, float], token: str) -> dict | None:
    try:
        coords = list(bar_data["geoData"]["coordinates"])
        coords.reverse()
        lat, lon = coords
    except (KeyError, TypeError, ValueError) as e:
        logging.error("Invalid bar data, skipping: %s", e)
        return None
    dist = get_distance_km(start_coords, coords)
    logging.info(f"{bar_data['Name']} - {dist}")
    bar_info = {
        "latidude": lat,
        "longtidude": lon,
        "name": bar_data["Name"],
        "distance": dist,
        "address": bar_data["Address"],
    }
    return bar_info


def get_nearest_bars(bars: list[dict], amount: int = 5) -> list[dict]:
    return sorted(bars, key=lambda b: b["distance"])[:amount]


def add_marker(
    location: tuple[float, float],
    out_map: folium.Map,
    text: str,
    icon: folium.Icon,
) -> None:
    folium.Marker(
        location=list(location),
        popup=text,
        tooltip=text,
        icon=icon,
    ).add_to(out_map)


def transfer_html(filepath: str = "index.html") -> str:
    return Path(filepath).read_text(encoding="utf-8")


def start_flask_server(func: callable, host: str, port: int) -> None:
    app = Flask(__name__)
    app.add_url_rule("/", "", func)
    app.run(host, port, debug=True)


def save_html_bars_map(bars: list[dict], my_address: tuple[float, float]) -> None:
    out_map = folium.Map(location=my_address, zoom_start=14)
    add_marker(my_address, out_map, "You are here!", folium.Icon(color="red"))
    for bar in bars:
        coords = bar["latidude"], bar["longtidude"]
        text = f"{bar['name']} - {bar['address']}"
        add_marker(coords, out_map, text, folium.Icon(color="green", icon="cloud"))
    out_map.save("index.html")


def draw_nearest_bars_map(location_address: str, bars_data: list[dict], token: str) -> None:
    coords = get_coordinates(location_address, token)
    if coords is None:
        raise ValueError(f"Could not find coordinates for: {location_address}")
    all_bars = []
    for bar_data in bars_data:
        info = get_bar_info(bar_data, coords, token)
        if info is not None:
            all_bars.append(info)
    nearest = get_nearest_bars(all_bars)
    save_html_bars_map(nearest, coords)


def get_args_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("my_address", nargs="+", help="My location address")
    parser.add_argument("-t", "--test", action="store_true", help="Test mode")
    return parser


def main() -> None:
    env = Env()
    env.read_env()
    logging.basicConfig(level=logging.ERROR)
    args = get_args_parser().parse_args()
    token = env.str("API_TOKEN")

    if not args.test and TEMP_FILE.exists():
        TEMP_FILE.unlink()

    my_address = " ".join(args.my_address)
    bars_data = json.loads(BARS_DB_FILE.read_text(encoding="utf-8"))

    draw_nearest_bars_map(my_address, bars_data, token)

    host, port = ("localhost", 8001) if platform.system() == "Windows" else ("0.0.0.0", 80)
    start_flask_server(transfer_html, host, port)


if __name__ == "__main__":
    main()
