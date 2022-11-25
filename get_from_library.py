import json
import os


def get_data(name):
    suffix = '.json'
    dir_path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(dir_path, os.path.join('libraries', name + suffix))
    with open(path, 'r') as file:
        return json.load(file)
