from selenium.common import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

DELAY = 5


def click_object_class_name(driver, address):
    waiter = WebDriverWait(driver, DELAY)
    waiter.until(EC.presence_of_element_located((By.CLASS_NAME, address)))
    waiter.until(EC.element_to_be_clickable((By.CLASS_NAME, address))).click()
    waiter.until(EC.presence_of_element_located((By.CLASS_NAME, address)))


def click_object_xpath(driver, address, ind):

    xpath = xpath_build(address, ind)

    waiter = WebDriverWait(driver, DELAY)
    waiter.until(EC.presence_of_element_located((By.XPATH, xpath)))
    waiter.until(EC.element_to_be_clickable((By.XPATH, xpath))).click()


def xpath_build(xpath, li_ind=1):
    s = xpath[::-1]
    ind = s.index('l')
    return xpath[:-ind + 2] + str(li_ind) + xpath[-ind + 3:]


def extend_all(driver, base_xpath):
    n = 1
    while True:
        try:
            # add a status bar?
            click_object_xpath(driver, base_xpath, n)
            n += 1
        except TimeoutException:
            break


def move_to_element(driver, address):
    element = driver.find_element(By.CLASS_NAME, address)
    actions = ActionChains(driver)  # move up to the very first element
    actions.move_to_element(element).perform()
