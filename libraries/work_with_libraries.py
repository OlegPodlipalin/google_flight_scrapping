import logging
import json
import os


def path_builder(filename):
    suffix = '.json'
    logging.debug(f'Creating OS path for {filename}.json')
    dir_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(dir_path, os.path.join('', filename + suffix))


def get_data(name):
    path = path_builder(name)
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


def save_to_json(name, data):
    path = path_builder(name)
    with open(path, 'w', encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    logging.info(f'Data saved to "{path}" library')
