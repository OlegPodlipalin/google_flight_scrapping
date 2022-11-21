from scraping import Scraper, extend_all

DELAY = 5  # import
SILENT_MODE = False  # import
SHOW_MORE_BUTTON = 'ZVk93d'  # class name of li object. to be imported for each site
LI_CLASS_NAME = 'pIav2d'  # class name of the first li object . to be imported for each site
LI_BUTTON_XPATH_TOP = '//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[3]/ul/li[1]/div/div[3]/div/div/button'
LI_BUTTON_XPATH_BOTTOM = '//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[5]/ul/li[1]/div/div[3]/div/div/button'


def main1(source):
    # source = 'https://www.google.com/travel/flights?q=' \
    #          'Flights%20to%20BER%20from%20TLV%20on%202022-12-25%20through%202022-12-31%20one-way&curr=EUR'
    scraper = Scraper(source, SILENT_MODE, DELAY)
    scraper.click_object_by_class_name(SHOW_MORE_BUTTON)
    scraper.move_to_element_by_class_name(LI_CLASS_NAME)
    soup = scraper.souping()
    amount_total = len(soup.findAll('li', class_=LI_CLASS_NAME))
    elements_to_be_extended = [LI_BUTTON_XPATH_TOP, LI_BUTTON_XPATH_BOTTOM]  #, LI_BUTTON_XPATH_BOTTOM]
    extend_all(scraper, elements_to_be_extended, amount_total, 'Berlin')  # import name of current destination
    return scraper.souping()


if __name__ == '__main__':
    source = 'https://www.google.com/travel/flights?q=' \
             'Flights%20to%20BER%20from%20TLV%20on%202022-12-25%20through%202022-12-31%20one-way&curr=EUR'
    main1(source)
