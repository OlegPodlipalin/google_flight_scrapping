from time import sleep
import re
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


def show_more_details(top_bottom_ind):
    ind = 1
    # li_xpath = LI_XPATH_1 + top_bottom_ind + LI_XPATH_2_1
    while True:
        try:
            x_path = MORE_DETAILS_BUTTON_1_1 + top_bottom_ind + MORE_DETAILS_BUTTON_1_2 + str(ind) + MORE_DETAILS_BUTTON_2
            WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.XPATH, x_path))).click()
            ind += 1
        except TimeoutException:
            break
    # return driver.find_elements(By.XPATH, li_xpath)


# DRIVER_PATH = 'C:/Users/backs/Documents/ITC/Project/google_flight_scrapping/chromedriver_win32/chromedriver.exe'
DELAY = 5
SHOW_MORE_BUTTON = '//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[5]/ul/li[last()]' #/div/span[1]/div/button'
LI_XPATH_1 = '//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div['
LI_XPATH_2_1 = ']/ul/li['
LI_XPATH_2_2 = ']'

# LI_XPATH_BOTTOM = '//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[5]/ul/li'
MORE_DETAILS_BUTTON_1_1 = f'//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div['
MORE_DETAILS_BUTTON_1_2 = ']/ul/li['
MORE_DETAILS_BUTTON_2 = ']/div/div[3]/div/div/button'
INDEX_TOP = '3'
INDEX_BOTTOM = '5'

# Run selenium driver and open the URL
options = Options()
# options.headless = True
# driver = webdriver.Chrome(executable_path=DRIVER_PATH, options=chrome_options)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.set_window_size(1920, 1080)
driver.get(
    'https://www.google.com/travel/flights?q=Flights%20to%20BER%20from%20TLV%20on%202022-12-25%20through%202022-12-31%20one-way&curr=EUR')

waiter = WebDriverWait(driver, DELAY)
# Open all the flights
waiter.until(EC.presence_of_element_located((By.XPATH, SHOW_MORE_BUTTON)))
waiter.until(EC.element_to_be_clickable((By.XPATH, SHOW_MORE_BUTTON))).click()
waiter.until(EC.presence_of_element_located((By.XPATH, SHOW_MORE_BUTTON)))
# waiter.until(EC.element_to_be_clickable((By.XPATH, SHOW_MORE_BUTTON)))  # This is the last element. If it is clickable - the webpage is ready

element = driver.find_element(By.XPATH, LI_XPATH_1 + INDEX_TOP + LI_XPATH_2_1 + '1' + LI_XPATH_2_2)
actions = ActionChains(driver)  # move up to the very first element
actions.move_to_element(element).perform()

""" 
here we got text which is hard to split according to the parameters order. 
###########################################################
flights_top = driver.find_elements(By.XPATH, LI_XPATH_TOP)
flights_bottom = driver.find_elements(By.XPATH, LI_XPATH_BOTTOM)
###########################################################
"""
# Implement STEP to scrape the site in parallel
show_more_details(INDEX_TOP)
# show_more_details(INDEX_BOTTOM)


element = driver.find_element(By.XPATH, LI_XPATH_1 + INDEX_TOP + LI_XPATH_2_1 + '1' + LI_XPATH_2_2)
actions = ActionChains(driver)  # move up to the very first element
actions.move_to_element(element).perform()

sleep(2)

s = BeautifulSoup(driver.page_source, "lxml")
li_elements = s.findAll('li', class_="pIav2d")

"""
This helps to get id of li element:
x = str(li_elements[0])
list_li = x.split()
id = [y for y in list_li[4].split('"') if len(y)][-1]
print(id)
"""
"""
this returns the ID and departure time (all of them) for li element:
print(len(li_elements))
x = str(li_elements[2])
list_li = x.split()
id = [y for y in list_li[4].split('"') if len(y)][-1]

dept_time = li_elements[2].findAll('div', class_="dPzsIb AdWm1c y52p7d")
print(len(dept_time))
print(dept_time[0].text.split()[0])
"""
"""
get id and departure time (all of them) for li element and create a new dictionary

{id: [{dept_time: <time>, arr_time: <time>, ...}, {dept_time: <time>, arr_time: <time>, ...}, {}, {}, {},  ...]}

d = {"dept_time": "dPzsIb AdWm1c y52p7d"}

x = str(li_elements[0])
list_li = x.split()
id = [y for y in list_li[4].split('"') if len(y)][-1]

dept_time = li_elements[0].findAll('div', class_=d['dept_time'])
print(dept_time[0].text)
print(dept_time[0].text.split()[2])

flight = {id: [{'dept_time': d_t.text.split()[0] + ' ' + d_t.text.split()[2]} for d_t in dept_time]}
print(flight)
"""
# id_s =




collapse_tags = s.findAll('div', class_=re.compile('^YMlIz FpEdX'))
collapse_tags2 = s.findAll('div', class_='YMlIz FpEdX')

# print(collapse_tags1[0].text)
# print(collapse_tags1[0].getText)
# print(type(s))
# print(type(collapse_tags1))
# print(len(collapse_tags2))



# for i in range(3):
#     flight_top = flights_top[i].text
# #     flight_bottom = flights_bottom[-i].text
#     print(f'top {i}:\t', [flight_top])
# #     print(f'bottom {-i}:\t', [flight_bottom])
# print(len(flights_top))
# # print(len(flights_bottom))

driver.quit()
