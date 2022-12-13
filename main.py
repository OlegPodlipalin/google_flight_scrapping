import gc
import logging
import threading
from itertools import repeat
from multiprocessing.pool import ThreadPool as Pool
from api import get_airports_codes
from cli import GetInput
from database_tools.databaser import DatabaseCreateWrite
from webpage_tools.driver import ChromedriverDriver
from webpage_tools.parser import GoogleFlightsParser
from webpage_tools.scraper import GoogleFlightsScraper
from libraries.get_from_library import get_data


logging.basicConfig(filename='gfs.log', encoding='utf-8', level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
threadLocal = threading.local()


def create_urls(user_input):
    parts = get_data('url_parts')
    urls = [parts['p1'] + user_input.data[dest] + parts['p2'] + term + parts['p3'] + user_input.args.flight_class +
            parts['p4'] for dest in user_input.args.dest for term in user_input.args.term]
    logging.info(f'URLs created fo the next directions and dates (class: {user_input.args.flight_class}): '
                 f'{[user_input.data[dest]for dest in user_input.args.dest]}'
                 f'{[term for term in user_input.args.term]}')
    return urls


def scrape(init_data):
    the_driver = getattr(threadLocal, 'the_driver', None)
    if the_driver is None:
        logging.info(f'Chromedriver instance not found. Creating new driver...')
        the_driver = ChromedriverDriver(init_data[0])
        setattr(threadLocal, 'the_driver', the_driver)
        logging.info(f'Chromedriver created and assigned as Thread local attribute')
    else:
        logging.info(f'Chromedriver instance found and assigned as Thread local attribute')
    soup = GoogleFlightsScraper(the_driver, init_data[1])
    trips = GoogleFlightsParser(soup.soup)
    return trips.trips


def main(source):
    user_input = GetInput()
    logging.info(f'Google_flights scraping script started')
    urls = create_urls(user_input)

    with Pool(4) as pool:
        logging.info(f'ThreadPool created')
        scr = zip(repeat(user_input), urls)
        destinations = pool.map(scrape, scr)

        global threadLocal
        del threadLocal
        gc.collect()

        pool.close()
        pool.join()

    logging.info(f'All the information from ThreadPool joined together and available for next processing')
    database = DatabaseCreateWrite()

    airports = get_airports_codes()
    database.write_from_api(airports)

    for trips in destinations:
        database.write_from_scrape(trips)


if __name__ == '__main__':
    url = 'https://www.google.com/travel/flights?q=Flights%20to%20BER%20from%20TLV%20on%202022-12-25%20%20with%20business%20class%20one-way&curr=EUR'  # %20one%20adult%20one%20children
    main(url)

# TODO: 4. add functionality to print out the flights
# TODO: 5. add functionality to export flights into .json file
