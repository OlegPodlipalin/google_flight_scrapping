from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from tqdm import tqdm
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Scraper:
    def __init__(self, url='https://www.google.com', silent_mode=True, delay=5):
        """
        Creates an instance of a class Scraper. This object is an instance of chromedriver with several methods to
        navigate on and interact with given webpage for webscraping purposes. Includes method to create a BeautifulSoup
        object.\n
        :param url: url of the webpage to be run by chromedriver
        :param silent_mode: option to run chromedriver in silent mode
        :param delay: time in seconds to wait before stopping chromedriver if an element on the page is not available
        """
        self._url = url
        self._silent_mode = silent_mode
        self._delay = delay
        self._start_driver()
        self._waiter = WebDriverWait(self.driver, self._delay)

    def _start_driver(self):
        options = Options()
        options.headless = self._silent_mode
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        if not self._silent_mode:
            driver.set_window_size(1920, 1080)
        driver.get(self._url)
        self.driver = driver
        print("the driver is started")

    def click_object_by_class_name(self, address):
        self._waiter.until(EC.presence_of_element_located((By.CLASS_NAME, address)))
        self._waiter.until(EC.element_to_be_clickable((By.CLASS_NAME, address))).click()

    def click_object_by_xpath(self, address):
        self._waiter.until(EC.presence_of_element_located((By.XPATH, address)))
        self._waiter.until(EC.element_to_be_clickable((By.XPATH, address))).click()

    def move_to_element_by_class_name(self, address):
        element = self._waiter.until(EC.presence_of_element_located((By.CLASS_NAME, address)))
        actions = ActionChains(self.driver)  # move up to the very first element
        actions.move_to_element(element).perform()

    def move_to_element_by_xpath(self, address):
        element = self._waiter.until(EC.presence_of_element_located((By.XPATH, address)))
        actions = ActionChains(self.driver)  # move up to the very first element
        actions.move_to_element(element).perform()

    def souping(self):
        sleep(1)
        return BeautifulSoup(self.driver.page_source, "lxml")


def address_builder(xpath, li_ind):
    ind = xpath[::-1].index('l')
    return xpath[:-ind + 2] + str(li_ind) + xpath[-ind + 3:]


def extend_all(driver, base_addresses, amount, destination):
    bar = tqdm(desc=f'{destination} destination scraping:', total=amount,
               bar_format="{desc:<10}{percentage:3.0f}%|{bar:50}{r_bar}")
    for base_address in base_addresses:
        for n in range(1, amount + 1):
            try:
                address = address_builder(base_address, n)
                # driver.move_to_element_by_xpath(address)
                driver.click_object_by_xpath(address)
                bar.update(1)
            except TimeoutException:
                break


def main():
    # source = 'https://www.google.com/travel/flights?q=' \
    #          'Flights%20to%20BER%20from%20TLV%20on%202022-12-25%20through%202022-12-31%20one-way&curr=EUR'
    # scraper = Scraper(source, False, DELAY)
    # scraper.click_object_by_class_name(SHOW_MORE_BUTTON)
    # scraper.move_to_element_by_class_name(LI_CLASS_NAME)
    # soup = scraper.souping()
    # amount_total = len(soup.findAll('li', class_=LI_CLASS_NAME))
    # elements_to_be_extended = [LI_BUTTON_XPATH_TOP, LI_BUTTON_XPATH_BOTTOM]
    # extend_all(scraper, elements_to_be_extended, amount_total, 'Berlin')  # import name of current destination
    # return scraper.souping()
    pass


if __name__ == '__main__':
    # print(len(main().findAll('li', class_="pIav2d")))
    pass

