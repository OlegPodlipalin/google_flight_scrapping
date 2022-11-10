from time import sleep

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

import driver_actions
import driver_start


def show_more_details(li_xpath):
    # ind = 1
    # li_xpath = LI_XPATH_TOP + top_bottom_ind + LI_XPATH_2
    # while True:
    #     try:
    #         x_path = MORE_DETAILS_BUTTON_1_1 + top_bottom_ind + MORE_DETAILS_BUTTON_1_2 + str(ind) + MORE_DETAILS_BUTTON_2
    #         WebDriverWait(driver, DELAY).until(EC.element_to_be_clickable((By.XPATH, x_path))).click()
    #         ind += 1
    #     except TimeoutException:
    #         break
    return driver.find_elements(By.XPATH, li_xpath)


# DRIVER_PATH = 'C:/Users/backs/Documents/ITC/Project/google_flight_scrapping/chromedriver_win32/chromedriver.exe'
DELAY = 5
SHOW_MORE_BUTTON = 'ZVk93d'  # class name of li object. to be imported for each site
LI_CLASS_NAME = 'pIav2d'  # class name of the first li object . to be imported for each site
LI_BUTTON_XPATH_TOP = '//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[3]/ul/li[1]/div/div[3]/div/div/button'
LI_BUTTON_XPATH_BOTTOM = '//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[5]/ul/li[1]/div/div[3]/div/div/button'

    # '//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[5]/ul/li[last()]/div/span[1]/div/button'
LI_XPATH_TOP = '//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[3]/ul/li'
LI_XPATH_BOTTOM = '//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[5]/ul/li'
# MORE_DETAILS_BUTTON_1_1 = f'//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div['
# MORE_DETAILS_BUTTON_1_2 = ']/ul/li['
# MORE_DETAILS_BUTTON_2 = ']/div/div[3]/div/div/button'
# MORE_DETAILS_BUTTON_INDEX_TOP = '3'
# MORE_DETAILS_BUTTON_INDEX_BOTTOM = '5'

# url should be imported
url = 'https://www.google.com/travel/flights?q=Flights%20to%20BER%20from%20TLV%20on%202022-12-25%20through%202022-12-31%20one-way&curr=EUR'

"""
1. to be deleted:

This piece of code in a module driver_setup.

options = Options()
# options.headless = True
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.set_window_size(1920, 1080)
driver.get(
    'https://www.google.com/travel/flights?q=Flights%20to%20BER%20from%20TLV%20on%202022-12-25%20through%202022-12-31%20one-way&curr=EUR')
"""
# driver start
driver = driver_start.start_driver(url, silent_mode=False)
# waiter = WebDriverWait(driver, DELAY)

"""
2. to be deleted:

This piece of code in a module driver_actions.

waiter.until(EC.presence_of_element_located((By.CLASS_NAME, SHOW_MORE_BUTTON)))
waiter.until(EC.element_to_be_clickable((By.CLASS_NAME, SHOW_MORE_BUTTON))).click()
waiter.until(EC.presence_of_element_located((By.CLASS_NAME, SHOW_MORE_BUTTON)))
# waiter.until(EC.element_to_be_clickable((By.XPATH, SHOW_MORE_BUTTON)))  # This is the last element. If it is clickable - the webpage is ready
"""
# open all the flights
driver_actions.click_object_class_name(driver, SHOW_MORE_BUTTON)
sleep(3)
"""
3. to be deleted:

This piece of code in a module driver_actions.

element = driver.find_element(By.XPATH, LI_XPATH_TOP)
actions = ActionChains(driver)  # move up to the very first element
actions.move_to_element(element).perform()
"""
# move up to the very first element
driver_actions.move_to_element(driver, LI_CLASS_NAME)

driver_actions.open_all(driver, LI_BUTTON_XPATH_TOP)
driver_actions.open_all(driver, LI_BUTTON_XPATH_BOTTOM)

s = BeautifulSoup(driver.page_source, "lxml")
li_elements = s.findAll('li', class_="pIav2d")

sleep(2)
flights_top = driver.find_elements(By.XPATH, LI_XPATH_TOP)
flights_bottom = driver.find_elements(By.XPATH, LI_XPATH_BOTTOM)

# for i in range(3):
#     flight_top = flights_top[i].text
#     flight_bottom = flights_bottom[-i].text
#     print(f'top {i}:\t', [flight_top])
#     print(f'bottom {-i}:\t', [flight_bottom])
print(len(flights_top))
print(len(flights_bottom))

driver.quit()
