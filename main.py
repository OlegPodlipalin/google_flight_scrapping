from functools import partial
from multiprocessing import Pool

from cli import GetInput
from parser import Parser
from scraper import Scraper
from get_from_library import get_data


def create_urls(user_input):
    parts = get_data('url_parts')
    urls = [parts['p1'] + user_input.data[dest] + parts['p2'] + term + parts['p3'] + user_input.args.flight_class +
            parts['p4'] for dest in user_input.args.dest for term in user_input.args.term]
    print(urls)
    return urls


def main(source):
    user_input = GetInput()
    urls = create_urls(user_input)
    with Pool(4) as pool:
        scr = partial(Scraper, user_input)
        pool.map(scr, urls)
    scraper = Scraper(user_input, url)  #############################################
    scraper.run()
    parser = Parser(scraper.soup)
    parser.run()
    for ind, flight in enumerate(parser.flights.items()):
        print(ind, '\t', flight)


if __name__ == '__main__':
    url = 'https://www.google.com/travel/flights?q=Flights%20to%20BER%20from%20TLV%20on%202022-12-25%20%20with%20business%20class%20one-way&curr=EUR'  # %20one%20adult%20one%20children
    main(url)
