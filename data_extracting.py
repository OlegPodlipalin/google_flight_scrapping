import scrapping

destinations = {1: 'PAR',
                2: 'BER',
                3: 'AMS',
                4: 'ROM',
                5: 'MAD'}

CHOOSE_YOUR_OPTION =   # 1 - Paris, 2 - Berlin, 3 - Amsterdam, 4 - Roma, 5 -Madrid
# CHOOSE_YOUR_OPTION_DAY = not ready yet. the same as with CHOOSE_YOUR_OPTION (destination)

attributes = {'Departure hour': 'dPzsIb AdWm1c y52p7d',
              'Arrival hour': 'SWFQlc AdWm1c y52p7d',
              'Flight duration': 'CQYfx y52p7d',
              'Connection time and location': 'tvtJdb eoY5cb y52p7d',
              'Company': 'Xsgmwe',
              'Flight number': 'Xsgmwe QS0io',
              'Price': 'YMlIz FpEdX',
              'Type of flight': 'J2OpGd sSHqwe',
              'CO2 emission of the flight': 'h6GTp'}

SCRAPPED_PARAMETERS = {"dept_time": "dPzsIb AdWm1c y52p7d"}

# to be imported
LI_CLASS_NAME = 'pIav2d'
flights = dict()
# source to be imported
source = f'https://www.google.com/travel/flights?q=Flights%20to%20{destinations[CHOOSE_YOUR_OPTION]}%20from%20TLV%20on%202022-12-20%20through%202022-12-30%20one-way&curr=EUR'

soup = scrapping.scrape_data(source)
li_elements = soup.findAll('li', class_=LI_CLASS_NAME)

li_string = [str(element).split() for element in li_elements]
flight_id_list = [li[4].split('"')[1] for li in li_string]  # indexes were checked manually on the site

for ind, li_element in enumerate(li_elements):
    flight_departure_time = li_element.findAll('div', class_=attributes['Departure hour'])
    departure_time = {'Departure hour': [d_time.text.split()[0] + ' ' + d_time.text.split()[2]
                      if d_time.text.split() else None
                      for d_time in flight_departure_time]}

    flight_arrival_time = li_element.findAll('div', class_=attributes['Arrival hour'])
    arrival_time = {'Arrival hour': [a_time.text.split()[0] + ' ' + a_time.text.split()[2]
                    if a_time.text.split() else None
                    for a_time in flight_arrival_time]}

    flight_duration = li_element.findAll('div', class_=attributes['Flight duration'])
    duration = {'Flight duration': [f_duration.text.split(':')[1].strip()
                if f_duration.text.split(':') else None
                for f_duration in flight_duration]}

    flight_price = li_element.findAll('div', class_=attributes['Price'])
    price = {'Price': str({f_price.text
             if f_price.text else None
             for f_price in flight_price})}

    flights[flight_id_list[ind]] = [departure_time, arrival_time, duration, price]

for ind, flight_id in enumerate(flights):
    print(ind, '\t', flight_id, flights[flight_id])
