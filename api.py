import json
import requests


KEY = '4746f9a2-bac2-4553-8927-e1c8815befd2'


def get_airports_codes():
    response = requests.request("GET", f'https://airlabs.co/api/v9/airports?api_key={KEY}')
    response_json = response.json()
    return [(item.get('iata_code'), item.get('name')) for item in response_json['response']
            if item.get('iata_code') is not None]


if __name__ == '__main__':
    airports = get_airports_codes()
    # save_to_json(airports)
    # for item in airports.items():
    #     print(item)
