import logging
import json
import os


def get_data(name):
    suffix = '.json'
    dir_path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(dir_path, os.path.join('', name + suffix))
    logging.info(f'Getting data from {name} library')
    try:
        logging.info(f'Opening {path}')
        with open(path, 'r') as file:
            result = json.load(file)
            logging.info(f'Data from "{name}" library extracted')
            return result
    except FileNotFoundError:
        logging.error(f'File not found: {path}')
        raise FileNotFoundError(f'File not found: {path}')
