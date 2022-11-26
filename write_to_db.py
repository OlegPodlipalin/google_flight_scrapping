from bs4 import BeautifulSoup
import pymysql.cursors
from datetime import date
import main

def write_flight_to_db(parser_flights):
    """
    Write flight details into DB
    """