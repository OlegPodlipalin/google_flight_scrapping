import gc
import logging
import threading
from time import time
from itertools import repeat
from multiprocessing.pool import ThreadPool as Pool
from selenium.common import TimeoutException, ElementClickInterceptedException
from api import get_airports_codes
from cli import GetInput
from database_tools.databaser import DatabaseCreateWrite
from webpage_tools.driver import ChromedriverDriver
from webpage_tools.parser import GoogleFlightsParser
from webpage_tools.scraper import GoogleFlightsScraper
from libraries.work_with_libraries import get_data


threadLocal = threading.local()
# setting config to logging module
logging.basicConfig(filename='gfs.log', encoding='utf-8', level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')


def create_urls(user_input):
    """
    Function takes in start parameters, creates and returns a list of URLs for scraping
    :param user_input: instance of GetInput class that contains start parameters
    :return: list of URLs for scraping
    """
    # getting parts of url from library url_parts.json
    parts = get_data('url_parts')
    # url creation
    urls = [parts['p1'] + user_input.data[dest] + parts['p2'] + term + parts['p3'] + user_input.args.flight_class +
            parts['p4'] for dest in user_input.args.dest for term in user_input.args.term]
    logging.info(f'URLs created for the next directions and dates (class: {user_input.args.flight_class}): '
                 f'{[user_input.data[dest]for dest in user_input.args.dest]} for '
                 f'{[term for term in user_input.args.term]}')
    return urls


def scrape(init_data):
    """
    Function creates a pipeline for getting data from Google Flights service with the help of ChromedriverDriver,
    GoogleFlightsScraper and GoogleFlightsParse instances. This function is intended to be called from ThreadPool
    :param init_data: tuple of two elements: start parameters and list of URLs for scraping
    :return: dictionary consists of trips scraped from specific URL
    """
    # attempt to get ChromedriverDriver instance from local Thread if it already exists
    the_driver = getattr(threadLocal, 'the_driver', None)
    if the_driver is None:
        # creation ChromedriverDriver instance and assigning it to a local Thread when it does not exist
        logging.info(f'Chromedriver instance not found. Creating new driver...')
        the_driver = ChromedriverDriver(init_data[0])
        setattr(threadLocal, 'the_driver', the_driver)
        logging.info(f'Chromedriver created and assigned as Thread local attribute')
    else:
        logging.info(f'Chromedriver instance found and assigned as Thread local attribute')

    for loop_num in range(1, 4):
        try:
            # sending ChromedriverDriver instance and list of URLs into GoogleFlightsScraper
            soup = GoogleFlightsScraper(the_driver, init_data[1])
        except ElementClickInterceptedException:
            # if element was not clickable
            if loop_num < 3:
                # there are 3 attempts to get data from webpage
                logging.warning(f'Element not clickable on {init_data[1].split("%20")[2]} on '
                                f'{init_data[1].split("%20")[6]}. Attempt {loop_num}')
                print(f'Issue with getting data from {init_data[1].split("%20")[2]} on {init_data[1].split("%20")[6]}. '
                      f'Trying again...')
            else:
                # stop trying on this webpage after 3 attempts
                logging.error(f'Cannot scrape {init_data[1].split("%20")[2]} on '
                              f'{init_data[1].split("%20")[6]}. Element not clickable ({loop_num} attempts)')
                print(f'Destination {init_data[1].split("%20")[2]} on {init_data[1].split("%20")[6]} was not scraped')
        except TimeoutException:
            # if element was not found and waiter time expired
            if loop_num < 3:
                # if element was not clickable
                logging.warning(f'Timeout exception while getting {init_data[1].split("%20")[2]} on '
                                f'{init_data[1].split("%20")[6]}. Attempt {loop_num}')
                print(f'Issue with getting data from {init_data[1].split("%20")[2]} on {init_data[1].split("%20")[6]}. '
                      f'Trying again...')
            else:
                # stop trying on this webpage after 3 attempts
                logging.error(f'Cannot scrape {init_data[1].split("%20")[2]} on {init_data[1].split("%20")[6]}. '
                              f'Timeout exception appeared ({loop_num} attempts)')
                print(f'Destination {init_data[1].split("%20")[2]} on {init_data[1].split("%20")[6]} was not scraped')
        else:
            # sending the result of scraping (BeautifulSoup class object) into GoogleFlightsParser to extract data
            trips = GoogleFlightsParser(soup.soup)
            return trips.trips
    # return None if there were exceptions while scraping webpage
    return None


def main():
    """
    Function runs all the parts of Google Flights scraping script. The function uses multiprocessing ThreadPool and
    can run up to 4 Threads simultaneously. Each Thread contains its own ChromedriverDriver instance which may be
    reused when number of destination-date options more than 4. As a result 'google_flights' database with scraped
    information will be created. In addition to this API request performs to get airports information.
    """
    start = time()
    print("Google Flights scraping script started")
    # extracting users input
    user_input = GetInput()
    logging.info(f'#########################################\nGoogle_flights scraping script started')
    # URLs creation
    urls = create_urls(user_input)

    # ThreadPool creation
    with Pool(4) as pool:
        print("Multiprocessing thread pool created")
        logging.info(f'ThreadPool created')
        # creation source variable 'src' that contains information for function scrape, because
        # ThreadPool .map() method allows takes in only one parameter for executed function
        scr = zip(repeat(user_input), urls)
        destinations = pool.map(scrape, scr)

        # memory cleaning and finishing multiprocessing.
        global threadLocal
        del threadLocal
        gc.collect()

        pool.close()
        pool.join()

    logging.info(f'All the information from ThreadPool joined together and available for next processing')
    # DatabaseCreateWrite instance creation, on this stage 'google_flights' database is created if it does not exist
    database = DatabaseCreateWrite()
    # getting airports data from API source
    airports = get_airports_codes()  # !!! ADD logging
    # writing airports data into database
    database.write_from_api(airports)

    # since multiprocessing implemented dictionaries of trips collected into destinations variable
    for trips in destinations:
        if trips is not None:
            # writing scraped data into database
            database.write_from_scrape(trips)

    logging.info(f'Total time for script execution: {time() - start} seconds')
    logging.info(f'#########################################\nGoogle_flights scraping script Finished successfully')


if __name__ == '__main__':
    # url = 'https://www.google.com/travel/flights?q=Flights%20to%20BER%20from%20TLV%20on%202022-12-25%20%20with%20business%20class%20one-way&curr=EUR'  # %20one%20adult%20one%20children
    main()
    pass
# TODO: 4. add functionality to print out the flights
# TODO: 5. add functionality to export flights into .json file
