import logging
from tqdm import tqdm
from time import sleep, time
from bs4 import BeautifulSoup
from selenium.common import TimeoutException, ElementClickInterceptedException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from libraries.work_with_libraries import get_data


class GoogleFlightsScraper:
    def __init__(self, driver, url):
        """
        Creates a GoogleFlightsScraper object. Accepts ChromedriverDriver instance and load in it URL provided.
        After loading URL automatically runs scraping algorithm. The result is the BeautifulSoup object contained in
        .soup parameter
        :param driver: ChromedriverDriver instance (should contain both the driver and selenium WebDriverWait instances)
        :param url: URL to scrape
        """
        logging.info('GoogleFlightsScraper instance creation...')
        # getting data from scraping_parsing.json library
        self._data = get_data('scraping_parsing')  # catch exceptions?

        # instance initialization
        self.soup = None
        self._number_elem_to_scrape = 0
        self._destination = f'{url.split("%20")[2]} on {url.split("%20")[6]}'
        self._webpage = f'(webpage: destination {url.split("%20")[2]}, ' \
                        f'date of flight: {url.split("%20")[6]}, class: {url.split("%20")[9]})'

        logging.info(f'Getting destination: {self._destination}')
        # loading URL
        print(f"Opening URL for {self._destination}...")
        driver.driver.get(url)
        logging.debug(f'Destination: {self._destination} loaded')
        self._driver = driver.driver
        self._waiter = driver.waiter
        logging.info(f'GoogleFlightsScraper instance created')

        self._run()

    def _click_object_by_class_name(self, address):
        """ 
        Private method for performing a click on a html object using its class name. Uses selenium WebDriverWait 
        instance to wait for the object to be clickable.
        :param address: class name of a html object 
        """
        logging.debug(f'Waiting for button "show more" to clickable for {self._webpage}')
        self._waiter.until(EC.presence_of_element_located((By.CLASS_NAME, address)))
        self._waiter.until(EC.element_to_be_clickable((By.CLASS_NAME, address))).click()
        logging.info(f'Button "show more" clicked on {self._webpage}')

    def _click_object_by_xpath(self, address):
        """
        Private method for performing a click on a html object using its xpath. Uses selenium WebDriverWait instance 
        to wait for the object to be clickable.
        :param address: xpath of a html object
        """
        logging.debug(f'Waiting for button "expand details" to clickable for {self._webpage}')
        self._move_to_element_by_xpath(address)
        self._waiter.until(EC.presence_of_element_located((By.XPATH, address)))
        self._waiter.until(EC.element_to_be_clickable((By.XPATH, address))).click()
        logging.debug(f'Button "expand details" clicked on {self._webpage}')

    def _move_to_element_by_class_name(self, address):
        """
        Private method for performing a scroll to a html element action using its class name. Uses selenium 
        WebDriverWait instance to locate presence of a html object.
        :param address: class name of a html object
        """
        logging.debug(f'Returning to the beginning of the {self._webpage}')
        element = self._waiter.until(EC.presence_of_element_located((By.CLASS_NAME, address)))
        actions = ActionChains(self._driver)
        actions.move_to_element(element).perform()
        logging.debug(f'Returning to the beginning of the {self._webpage} successful')

    def _move_to_element_by_xpath(self, address):
        """
        Private method for performing a scroll to a html element action using its xpath. Uses selenium 
        WebDriverWait instance to locate presence of a html object.
        :param address: xpath of a html object 
        """
        logging.debug(f'Returning to the beginning of the {self._webpage}')
        element = self._waiter.until(EC.presence_of_element_located((By.XPATH, address)))
        actions = ActionChains(self._driver)
        actions.move_to_element(element).perform()
        logging.debug(f'Returning to the beginning of the {self._webpage} successful')

    def _souping(self):
        """
        Private method for collecting data from a webpage in a BeautifulSoup object. Besides BeautifulSoup object 
        includes in .soup parameter full description of a current webpage and short description of a destination. 
        In addition, calculates total number of trip element on a webpage.
        """
        # sleep time allows webpage structure to be completely loaded before html code parsing
        sleep(1)
        logging.debug(f'Getting BeautifulSoup from {self._webpage}')
        self.soup = (BeautifulSoup(self._driver.page_source, "lxml"), self._webpage, self._destination)
        logging.debug(f'Got BeautifulSoup from {self._webpage}')
        # calculating number of element on a webpage
        self._number_elem_to_scrape = len(self.soup[0].findAll('li', class_=self._data['li_class_name']))
        logging.debug(f'Number of elements to scrape on {self._webpage}: {self._number_elem_to_scrape}')

    def _address_builder(self, loc_ind, li_ind):
        """
        Private method for building xpath for 'expand' button elements.
        :param loc_ind: index of trips group location
        :param li_ind: index of html li element (trip row)
        :return: xpath of 'expand' button elements
        """
        xpath = self._data['button_head'] + str(loc_ind) + \
                self._data['button_body'] + str(li_ind) + self._data['button_tail']
        logging.debug(f'XPATH {xpath} for {self._webpage} created')
        return xpath

    def _run(self):
        """
        Private method to run the web page scraping algorithm
        """
        logging.debug(f"Start processing {self._webpage}")
        start = time()
        for loop in range(2):
            try:
                # opening all options to flight to be shown
                self._click_object_by_class_name(self._data['show_more_button'])
                self._move_to_element_by_class_name(self._data['li_class_name'])
            except TimeoutException:
                if loop == 1:
                    # for the first time try to wait 5 more seconds
                    logging.warning(f'TimeoutException occurred on {self._webpage}. Waiting extra 5 seconds')
                    sleep(5)
                else:
                    # for the second time stop algorithm
                    logging.error(f'TimeoutException occurred on {self._webpage} second time. Exception raised')
                    raise TimeoutException()
            except ElementClickInterceptedException:
                if loop == 1:
                    # for the first time try to wait 5 more seconds
                    logging.warning(f'ElementClickInterceptedException occurred on {self._webpage}.'
                                    f' Waiting extra 5 seconds')
                    sleep(5)
                else:
                    # for the second time stop algorithm
                    logging.error(f'ElementClickInterceptedException occurred on {self._webpage} second time. '
                                  f'Exception raised')
                    raise ElementClickInterceptedException()
            else:
                # if there were no exceptions break loop
                break
        # collecting information about total number of elements
        self._souping()
        logging.info(f'Number of elements to scrape on {self._webpage}: {self._number_elem_to_scrape}')

        logging.info(f'Start of extending flight details on {self._webpage}')
        bar = tqdm(desc=f'{self._destination} scraping', total=self._number_elem_to_scrape)
        # expanding all the trips to be able to scrape all the information
        # due to different webpage structure options there are 4 variants of trip groups locations on the web page
        for location_ind in [3, 4, 5, 6]:
            # expanding all the trips in the location with 'base_address' xpath by clicking on the 'expand' button
            for n in range(1, self._number_elem_to_scrape + 1):
                logging.debug(f'Opening element {n} in location {location_ind} on {self._webpage}')
                try:
                    self._click_object_by_xpath(self._address_builder(location_ind, n))
                    bar.update(1)
                except TimeoutException:
                    # catching this exception allows to continue expanding trips with different xpath address
                    logging.warning(f'Attempt to open element {n} on {self._webpage} - TimeoutException')
                    break

        logging.info(f'All {self._number_elem_to_scrape} elements on {self._webpage} extended')
        # creating BeautifulSoup object
        self._souping()
        logging.info(f'GoogleFlightsScraper finished to process {self._webpage} in {time() - start} seconds')


def main():
    # source = 'https://www.google.com/travel/flights?q=Flights%20to%20BER%20from%20TLV
    # %20on%202022-12-25%20%20with%20business%20class%20one-way&curr=EUR'  # %20one%20adult%20one%20children
    # user_input = GetInput()
    # scraper = GoogleFlightsScraper(user_input, source)
    # scraper._run()
    # with open('soup.txt', 'w') as file:
    #     file.write(scraper.soup)
    pass


if __name__ == '__main__':
    main()
