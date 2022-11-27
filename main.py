from parser import Parser
from scraper import Scraper
import write_to_db
import create_db

DELAY = 10  # import
SILENT_MODE = False  # import
SHOW_MORE_BUTTON = 'ZVk93d'  # class name of li object. to be imported for each site
LI_CLASS_NAME = 'pIav2d'  # class name of the first li object . to be imported for each site
LI_BUTTON_XPATH_TOP = '//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[3]/ul/li[1]/div/div[3]/div/div/button'
LI_BUTTON_XPATH_BOTTOM = '//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[5]/ul/li[1]/div/div[3]/div/div/button'


def main(source):
    # source = 'https://www.google.com/travel/flights?q=' \
    #      'Flights%20to%20BER%20from%20TLV%20on%202022-12-25%20through%202022-12-31%20one-way&curr=EUR'
    scraper = Scraper(source, SILENT_MODE, DELAY)
    scraper.run()
    parser = Parser(scraper.soup)
    parser.run()
    #Create DB
    create_db()
    #Inserting data collected from parser to database
    write_to_db.write_data_to_db(parser.flights)
    exit()
    for ind, flight in enumerate(parser.flights.items()):
        print(ind, '\t', flight)


if __name__ == '__main__':
    source = 'https://www.google.com/travel/flights?q=' \
             'Flights%20to%20BER%20from%20TLV%20on%202022-12-25%20through%202022-12-31%20one-way&curr=EUR'
    main(source)
