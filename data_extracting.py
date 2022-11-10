import scrapping


SCRAPPED_PARAMETERS = {"dept_time": "dPzsIb AdWm1c y52p7d"}
# SCRAPPED_PARAMETERS = {"dept_time": "zxVSec YMlIz tPgKwe ogfYpf"}

# to be imported
LI_CLASS_NAME = 'pIav2d'
flights = dict()
# source to be imported
source = 'https://www.google.com/travel/flights?q=' \
             'Flights%20to%20BER%20from%20TLV%20on%202022-12-20%20through%202022-12-30%20one-way&curr=EUR'

soup = scrapping.scrape_data(source)
li_elements = soup.findAll('li', class_=LI_CLASS_NAME)

li_string = [str(element).split() for element in li_elements]
flight_id_list = [li[4].split('"')[1] for li in li_string]  # indexes were checked manually on the site

for ind, li_element in enumerate(li_elements):
    flight_departure_time = li_element.findAll('div', class_=SCRAPPED_PARAMETERS['dept_time'])
    departure_time = [{'dept_time': d_time.text.split()[0] + ' ' + d_time.text.split()[2]}
                      if d_time.text.split() else None for d_time in flight_departure_time]
    flights[flight_id_list[ind]] = departure_time

for ind, flight_id in enumerate(flights):
    print(ind, '\t', flight_id, flights[flight_id])
