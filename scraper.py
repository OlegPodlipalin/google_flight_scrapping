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
from cli import GetInput

SHOW_MORE_BUTTON = 'ZVk93d'  # class name of li object. to be imported for each site
LI_CLASS_NAME = 'pIav2d'  # class name of the first li object . to be imported for each site
LI_BUTTON_1 = '//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[3]/ul/li[1]/div/div[3]/div/div/button'
LI_BUTTON_2 = '//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[4]/ul/li[1]/div/div[3]/div/div/button'
LI_BUTTON_3 = '//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[5]/ul/li[1]/div/div[3]/div/div/button'
LI_BUTTON_4 = '//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[6]/ul/li[1]/div/div[3]/div/div/button'


class Driver:
    def __init__(self, user_input):
        options = Options()
        options.headless = user_input.args.silent
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.set_window_size(1920, 1080)
        self.driver = driver
        self.waiter = WebDriverWait(self.driver, user_input.args.wait)


class Scraper:
    def __init__(self, driver, url):
        """
        Creates an instance of a class Scraper. This object is an instance of chromedriver with several methods to
        navigate on and interact with given webpage for webscraping purposes. Includes method to create a BeautifulSoup
        object.\n
        :param url: url of the webpage to be run by chromedriver
        :param silent_mode: option to run chromedriver in silent mode
        :param delay: time in seconds to wait before stopping chromedriver if an element on the page is not available
        """
        driver.driver.get(url)
        self._driver = driver.driver
        self._waiter = driver.waiter
        self.soup = None
        self._amount_elem_to_scrape = 0
        self._elements_to_be_extended = [LI_BUTTON_1, LI_BUTTON_2, LI_BUTTON_3, LI_BUTTON_4]
        self._destination = ''

        self.run()

    def _click_object_by_class_name(self, address):
        self._waiter.until(EC.presence_of_element_located((By.CLASS_NAME, address)))
        self._waiter.until(EC.element_to_be_clickable((By.CLASS_NAME, address))).click()

    def _click_object_by_xpath(self, address):
        self._move_to_element_by_xpath(address)
        self._waiter.until(EC.presence_of_element_located((By.XPATH, address)))
        self._waiter.until(EC.element_to_be_clickable((By.XPATH, address))).click()

    def _move_to_element_by_class_name(self, address):
        element = self._waiter.until(EC.presence_of_element_located((By.CLASS_NAME, address)))
        actions = ActionChains(self._driver)  # move up to the very first element
        actions.move_to_element(element).perform()

    def _move_to_element_by_xpath(self, address):
        element = self._waiter.until(EC.presence_of_element_located((By.XPATH, address)))
        actions = ActionChains(self._driver)  # move up to the very first element
        actions.move_to_element(element).perform()

    def _souping(self):
        sleep(1)
        self.soup = BeautifulSoup(self._driver.page_source, "lxml")
        self._amount_elem_to_scrape = len(self.soup.findAll('li', class_=LI_CLASS_NAME))

    @staticmethod
    def _address_builder(xpath, li_ind):
        ind = xpath[::-1].index('l')
        return xpath[:-ind + 2] + str(li_ind) + xpath[-ind + 3:]

    def run(self):
        self._click_object_by_class_name(SHOW_MORE_BUTTON)
        self._move_to_element_by_class_name(LI_CLASS_NAME)
        self._souping()

        bar = tqdm(desc=f'{self._destination} destination scraping', total=self._amount_elem_to_scrape)  # bar_format="{desc:<10}{percentage:3.0f}%|{bar:50}{r_bar}"
        for base_address in self._elements_to_be_extended:
            for n in range(1, self._amount_elem_to_scrape + 1):
                try:
                    self._click_object_by_xpath(self._address_builder(base_address, n))
                    bar.update(1)
                except TimeoutException:
                    break

        self._souping()


def main():
    source = 'https://www.google.com/travel/flights?q=Flights%20to%20BER%20from%20TLV%20on%202022-12-25%20%20with%20business%20class%20one-way&curr=EUR'  # %20one%20adult%20one%20children
    user_input = GetInput()
    scraper = Scraper(user_input, source)
    scraper.run()
    with open('soup.txt', 'w') as file:
        file.write(scraper.soup)


if __name__ == '__main__':
    main()
