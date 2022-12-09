import gc
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


threadLocal = threading.local()


def create_urls(user_input):
    parts = get_data('url_parts')
    urls = [parts['p1'] + user_input.data[dest] + parts['p2'] + term + parts['p3'] + user_input.args.flight_class +
            parts['p4'] for dest in user_input.args.dest for term in user_input.args.term]
    return urls


def scrape(init_data):
    the_driver = getattr(threadLocal, 'the_driver', None)
    if the_driver is None:
        the_driver = ChromedriverDriver(init_data[0])
        setattr(threadLocal, 'the_driver', the_driver)
    soup = GoogleFlightsScraper(the_driver, init_data[1])
    flight = GoogleFlightsParser(soup.soup)
    return flight.flights


def main(source):
    user_input = GetInput()
    urls = create_urls(user_input)

    with Pool(4) as pool:
        scr = zip(repeat(user_input), urls)
        flights = pool.map(scrape, scr)

        global threadLocal
        del threadLocal
        gc.collect()

        pool.close()
        pool.join()

    database = DatabaseCreateWrite()

    airports = get_airports_codes()
    database.write_from_api(airports)

    for flight in flights:
        database.write_from_scrape(flight)


if __name__ == '__main__':
    url = 'https://www.google.com/travel/flights?q=Flights%20to%20BER%20from%20TLV%20on%202022-12-25%20%20with%20business%20class%20one-way&curr=EUR'  # %20one%20adult%20one%20children
    main(url)

# TODO: 1. rewrite parser.py so that it holds just one flight per instance.
# TODO: 2. add to Scraper arguments to show in status-bar
# TODO: 3. move all the constant variables to libraries
# TODO: 4. add functionality to print out the flights
# TODO: 5. add functionality to export flights into .json file
# TODO: 6. check the date to be > today
