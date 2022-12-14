import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait


class ChromedriverDriver:
    def __init__(self, user_input):
        """
        Creates a new Chromedriver instance. Two parameters may be changed: headless mode (True or False) and timeout
        parameter for selenium WebDriverWait instance. If headless mode is False, window size will be determined
        automatically (1920x1080).
        :param user_input: argparse (GetInput) class object
        """
        logging.info(f'ChromedriverDriver instance creation...')
        options = Options()
        # silent (headless) mode settings applied
        options.headless = user_input.args.silent
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        logging.debug(f'Settings for Chromedriver: headless - {user_input.args.silent}, delay: {user_input.args.wait}')
        # driver creation. chromedriver is downloaded automatically
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        logging.info(f'Chromedriver instance created')
        driver.set_window_size(1920, 1080)
        logging.debug(f'Chromedriver window size set to 1920x1080')
        self.driver = driver
        self.waiter = WebDriverWait(self.driver, user_input.args.wait)
        logging.info(f'ChromedriverDriver instance created')

    def __del__(self):
        """
        This method is called when the driver is no longer needed. Finishes the Chromedriver workflow.
        """
        self.driver.quit()
        logging.info(f'ChromedriverDriver instance deleted')
