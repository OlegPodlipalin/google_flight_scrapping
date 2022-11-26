from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait


class ChromedriverDriver:
    def __init__(self, user_input):
        options = Options()
        options.headless = user_input.args.silent
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.set_window_size(1920, 1080)
        self.driver = driver
        self.waiter = WebDriverWait(self.driver, user_input.args.wait)

    def __del__(self):
        self.driver.quit()
