import logging
from tqdm import tqdm
from time import sleep
from bs4 import BeautifulSoup
from selenium.common import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from libraries.get_from_library import get_data


class GoogleFlightsScraper:
    def __init__(self, driver, url):
        """

        :param driver:
        :param url:
        """
        logging.info('GoogleFlightsScraper instance creation...')
        self._data = get_data('scraping_parsing')
        self._destination = f'{url.split("%20")[2]} on {url.split("%20")[6]}'
        self._webpage = f'(webpage: destination {url.split("%20")[2]}, ' \
                        f'date of flight: {url.split("%20")[6]}, class: {url.split("%20")[9]})'
        logging.info(f'Getting destination: {self._destination}')
        driver.driver.get(url)
        logging.debug(f'Destination: {self._destination} loaded successfully')
        self._driver = driver.driver
        self._waiter = driver.waiter
        self.soup = None
        self._amount_elem_to_scrape = 0
        self._extend_elements = [self._data['button_head'] + str(n) + self._data['button_tail'] for n in range(3, 7)]
        logging.info(f'GoogleFlightsScraper instance created')

        self._run()

    def _click_object_by_class_name(self, address):
        logging.debug(f'Waiting for button "show more" to clickable for {self._webpage}')
        self._waiter.until(EC.presence_of_element_located((By.CLASS_NAME, address)))
        self._waiter.until(EC.element_to_be_clickable((By.CLASS_NAME, address))).click()
        logging.debug(f'Button "show more" clicked on {self._webpage}')

    def _click_object_by_xpath(self, address):
        logging.debug(f'Waiting for button "expand details" to clickable for {self._webpage}')
        self._move_to_element_by_xpath(address)
        self._waiter.until(EC.presence_of_element_located((By.XPATH, address)))
        self._waiter.until(EC.element_to_be_clickable((By.XPATH, address))).click()
        logging.debug(f'Button "expand details" clicked on {self._webpage}')

    def _move_to_element_by_class_name(self, address):
        logging.debug(f'Returning to the beginning of the {self._webpage}')
        element = self._waiter.until(EC.presence_of_element_located((By.CLASS_NAME, address)))
        actions = ActionChains(self._driver)  # move up to the very first element
        actions.move_to_element(element).perform()
        logging.debug(f'Returning to the beginning of the {self._webpage} successful')

    def _move_to_element_by_xpath(self, address):
        logging.debug(f'Returning to the beginning of the {self._webpage}')
        element = self._waiter.until(EC.presence_of_element_located((By.XPATH, address)))
        actions = ActionChains(self._driver)  # move up to the very first element
        actions.move_to_element(element).perform()
        logging.debug(f'Returning to the beginning of the {self._webpage} successful')

    def _souping(self):
        logging.debug(f'Getting BeautifulSoup from {self._webpage}')
        sleep(1)
        self.soup = (BeautifulSoup(self._driver.page_source, "lxml"), self._webpage, self._destination)
        logging.debug(f'Got BeautifulSoup from {self._webpage}')
        self._amount_elem_to_scrape = len(self.soup[0].findAll('li', class_=self._data['li_class_name']))
        logging.debug(f'Number of elements to scrape on {self._webpage}: {self._amount_elem_to_scrape}')

    def _address_builder(self, xpath, li_ind):
        ind = xpath[::-1].index('l')
        logging.debug(f'XPATH {xpath[:-ind + 2] + str(li_ind) + xpath[-ind + 3:]} for {self._webpage} created')
        return xpath[:-ind + 2] + str(li_ind) + xpath[-ind + 3:]

    def _run(self):
        logging.debug(f"Start processing {self._webpage}")
        self._click_object_by_class_name(self._data['show_more_button'])
        self._move_to_element_by_class_name(self._data['li_class_name'])
        self._souping()
        logging.info(f'Number of elements to scrape on {self._webpage}: {self._amount_elem_to_scrape}')

        logging.info(f'Start of extending flight details on {self._webpage}')
        bar = tqdm(desc=f'{self._destination} scraping', total=self._amount_elem_to_scrape)
        for base_address in self._extend_elements:
            for n in range(1, self._amount_elem_to_scrape + 1):
                logging.debug(f'Opening element {n} on {self._webpage}')
                try:
                    self._click_object_by_xpath(self._address_builder(base_address, n))
                    bar.update(1)
                except TimeoutException:
                    logging.warning(f'Attempt to open element {n} on {self._webpage} - TimeoutException')
                    break

        logging.info(f'All elements on {self._webpage} extended')
        self._souping()
        logging.info(f'GoogleFlightsScraper finish to process {self._webpage}')


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
