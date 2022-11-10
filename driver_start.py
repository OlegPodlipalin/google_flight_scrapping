from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def start_driver(url='http://www.google.com', silent_mode=True):  # try except with silent_mode and url types!!
    # url = 'https://www.google.com/travel/flights?q=Flights%20to%20BER%20from%20TLV%20on%202022-12-25%20through%202022-12-31%20one-way&curr=EUR'
    options = Options()
    options.headless = silent_mode
    web_driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    web_driver.set_window_size(1920, 1080)
    web_driver.get(url)
    print("the driver is started")
    return web_driver


if __name__ == '__main__':
    driver = start_driver(silent_mode=False)
    sleep(5)
    driver.quit()
    print("the driver is stopped")
