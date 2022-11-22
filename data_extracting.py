from main import main
from datetime import time

DESTINATIONS = {1: 'PAR',
                2: 'BER',
                3: 'AMS',
                4: 'ROM',
                5: 'MAD'}

CHOOSE_YOUR_OPTION = 2  # 1 - Paris, 2 - Berlin, 3 - Amsterdam, 4 - Roma, 5 -Madrid
# CHOOSE_YOUR_OPTION_DAY = not ready yet. the same as with CHOOSE_YOUR_OPTION (destination)

ATTRIBUTES = {'Departure': ['div', 'dPzsIb AdWm1c y52p7d'],
              'Arrival': ['div', 'SWFQlc AdWm1c y52p7d'],
              'Flight duration': ['div', 'CQYfx y52p7d'],
              # 'Connection time': ['div', 'tvtJdb eoY5cb y52p7d'],
              'Price': ['div', 'YMlIz FpEdX'],
              'CO2 emission': ['span', 'gI4d6d'],
              'Facilities': [['ul', 'li'], ['elO9Ce sSHqwe JNp8ff', 'WtSsrd']]}

# {'Company': 'Xsgmwe', 'Flight number': 'Xsgmwe QS0io', 'Type of flight': 'J2OpGd sSHqwe'} hard to scrape

SCRAPPED_PARAMETERS = {"dept_time": "dPzsIb AdWm1c y52p7d"}

# to be imported
LI_CLASS_NAME = 'pIav2d'
flights = dict()
# source to be imported
source = f'https://www.google.com/travel/flights?q=Flights%20to%20{DESTINATIONS[CHOOSE_YOUR_OPTION]}%20from%20TLV%20on%202022-12-20%20through%202022-12-30%20one-way&curr=EUR'


def get_element(element, attribute_name):
    return element.findAll(ATTRIBUTES[attribute_name][0], class_=ATTRIBUTES[attribute_name][1])


def get_departure_arrival(flight):
    flight_time = []
    flight_airport = []

    for flight_elements in flight:
        if not flight_elements:
            flight_time.append(None)
            flight_airport.append(None)
            continue

        flight_element_splited = flight_elements.text.split()
        hours_minutes = flight_element_splited[0].split(':')
        airport = flight_element_splited[-1].strip('()')  # TODO: how can be processed (need full name of an airport)

        if flight_element_splited[2] == 'PM' and hours_minutes[0] != '12':
            hours = int(hours_minutes[0]) + 12
        elif flight_element_splited[2] == 'AM' and hours_minutes[0] == '12':
            hours = 0
        else:
            hours = int(hours_minutes[0])
        minutes = int(hours_minutes[1])

        flight_time.append(time(hours, minutes))  # what formate of time is better to store in database?
        flight_airport.append(airport)
    return flight_time, flight_airport


def time_components_checker(elements):
    if elements[1] != 'h':
        hours = 0
        minutes = int(elements[0])
    elif len(elements) < 3:
        hours = int(elements[0])
        minutes = 0
    else:
        hours = int(elements[0])
        minutes = int(elements[2])
    return hours, minutes


def get_flight_duration(flight):
    flight_duration = []
    for flight_elements in flight:
        if not flight_elements:
            flight_duration.append(None)
            continue
        duration_elements = flight_elements.text.split(':')[1].split()
        hours, minutes = time_components_checker(duration_elements)
        flight_duration.append(time(hours, minutes))  # what formate of time is better to store in database?
    return flight_duration


def get_stop_duration(flight):
    stop_duration = []
    for flight_elements in flight:
        if not flight_elements:
            stop_duration.append(None)
            continue
        stop_elements = flight_elements.text.split()
        hours, minutes = time_components_checker(stop_elements)
        stop_duration.append(time(hours, minutes))  # what formate of time is better to store in database?
    return stop_duration


def get_price(flight):
    price = None
    for flight_elements in flight:
        if flight_elements:
            price = flight_elements.text  # TODO get integer!!
            break
    return price


def get_co2_emission(flight):
    co2_emission = []
    for flight_elements in flight:
        if not flight_elements:
            co2_emission.append(None)
            continue
        co2_emission.append(flight_elements.text.split()[-2])
    return co2_emission


soup = main(source)
li_elements = soup.findAll('li', class_=LI_CLASS_NAME)

li_string = [str(element).split() for element in li_elements]
flight_id_list = [li[4].split('"')[1] for li in li_string]  # indexes were checked manually on the site

for ind, li_element in enumerate(li_elements):

    departure_time, departure_airport = get_departure_arrival(get_element(li_element, 'Departure'))
    departure_info = {'Departure_hour': departure_time} | {'Departure_airport': departure_airport}

    arrival_time, arrival_airport = get_departure_arrival(get_element(li_element, 'Arrival'))
    arrival_info = {'Arrival_hour': arrival_time} | {'Arrival_airport': arrival_airport}

    duration = get_flight_duration(get_element(li_element, 'Flight duration'))
    duration_info = {'Flight duration': duration}  # TODO: check bugs here

    # connection = get_stop_duration(get_element(li_element, 'Connection time'))
    # connection_info = {'Stop duration': connection}

    price = get_price(get_element(li_element, 'Price'))
    price_info = {'Price': price}

    co2_emission = get_co2_emission(get_element(li_element, 'CO2 emission'))
    co2_emission_info = {'CO2 emission': co2_emission}

    # TODO: convert to function:
    flight_facilities = li_element.findAll(ATTRIBUTES['Facilities'][0][0], class_=ATTRIBUTES['Facilities'][1][0])
    facilities = {'Facilities': [
        [facility.text for facility in
         f_facility.findAll(ATTRIBUTES['Facilities'][0][1], class_=ATTRIBUTES['Facilities'][1][1])
         if not facility.text[:6] == 'Carbon'] for f_facility in flight_facilities]}

    flights[flight_id_list[ind]] = \
        departure_info | arrival_info | duration_info | price_info | co2_emission_info | facilities  # connection_info |

for ind, flight in enumerate(flights.items()):
    print(ind, '\t', flight)
