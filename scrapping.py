from time import sleep
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import driver_actions
import driver_start

SHOW_MORE_BUTTON = 'ZVk93d'  # class name of li object. to be imported for each site
LI_CLASS_NAME = 'pIav2d'  # class name of the first li object . to be imported for each site
LI_BUTTON_XPATH_TOP = '//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[3]/ul/li[1]/div/div[3]/div/div/button'
LI_BUTTON_XPATH_BOTTOM = '//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[5]/ul/li[1]/div/div[3]/div/div/button'

LI_XPATH_TOP = '//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[3]/ul/li'
LI_XPATH_BOTTOM = '//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[5]/ul/li'


def scrape_data(url='https://www.google.com'):  # url should be imported
    # driver start
    driver = driver_start.start_driver(url, silent_mode=False)

    # load all the flights
    driver_actions.click_object_class_name(driver, SHOW_MORE_BUTTON)

    # move up to the very first element
    driver_actions.move_to_element(driver, LI_CLASS_NAME)

    # extend all the flights
    driver_actions.extend_all(driver, LI_BUTTON_XPATH_TOP)
    driver_actions.extend_all(driver, LI_BUTTON_XPATH_BOTTOM)

    # move up to the very first element
    driver_actions.move_to_element(driver, LI_CLASS_NAME)
    sleep(2)
    soup = BeautifulSoup(driver.page_source, "lxml")
    li_elements = soup.findAll('li', class_="pIav2d")

    print(f'BeautifulSoup collects {len(li_elements)} flights')

    return soup


if __name__ == '__main__':
    source = 'https://www.google.com/travel/flights?q=' \
             'Flights%20to%20BER%20from%20TLV%20on%202022-12-25%20through%202022-12-31%20one-way&curr=EUR'
    s = scrape_data(source)
