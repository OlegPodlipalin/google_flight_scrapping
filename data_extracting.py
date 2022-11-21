from main import main1
from datetime import time

destinations = {1: 'PAR',
                2: 'BER',
                3: 'AMS',
                4: 'ROM',
                5: 'MAD'}

CHOOSE_YOUR_OPTION = 2  # 1 - Paris, 2 - Berlin, 3 - Amsterdam, 4 - Roma, 5 -Madrid
# CHOOSE_YOUR_OPTION_DAY = not ready yet. the same as with CHOOSE_YOUR_OPTION (destination)

ATTRIBUTES = {'Departure': ['div', 'dPzsIb AdWm1c y52p7d'],
              'Arrival': ['div', 'SWFQlc AdWm1c y52p7d'],
              'Flight duration': ['div', 'CQYfx y52p7d'],
              'Connection time': ['div', 'tvtJdb eoY5cb y52p7d'],
              'Price': ['div', 'YMlIz FpEdX'],
              'CO2 emission': ['span', 'gI4d6d'],
              'Facilities': [['ul', 'li'], ['elO9Ce sSHqwe JNp8ff', 'WtSsrd']]}

# {'Company': 'Xsgmwe', 'Flight number': 'Xsgmwe QS0io', 'Type of flight': 'J2OpGd sSHqwe'} hard to scrape

SCRAPPED_PARAMETERS = {"dept_time": "dPzsIb AdWm1c y52p7d"}

# to be imported
LI_CLASS_NAME = 'pIav2d'
flights = dict()
# source to be imported
source = f'https://www.google.com/travel/flights?q=Flights%20to%20{destinations[CHOOSE_YOUR_OPTION]}%20from%20TLV%20on%202022-12-20%20through%202022-12-30%20one-way&curr=EUR'


def get_element(element, attribute_name):
    return element.findAll(ATTRIBUTES[attribute_name][0], class_=ATTRIBUTES[attribute_name][1])


def get_departure_arrival(flight):
    # flight = element.fildAll(ATTRIBUTES[attribute_name][0], class_=ATTRIBUTES[attribute_name][1])
    flight_time = []
    flight_airport = []
    for flight_elements in flight:
        if not flight_elements:
            flight_time.append(None)
            flight_airport.append(None)
            continue
        flight_element_splited = flight_elements.text.split()
        hours_minutes = flight_element_splited[0].split(':')
        if flight_element_splited[2] == 'PM' and hours_minutes[0] != '12':
            hours = int(hours_minutes[0]) + 12
        elif flight_element_splited[2] == 'AM' and hours_minutes[0] == '12':
            hours = 0
        else:
            hours = int(hours_minutes[0])
        minutes = int(hours_minutes[1])
        airport = flight_element_splited[-1].strip('()')
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
    # flight = element.fildAll(ATTRIBUTES[attribute_name][0], class_=ATTRIBUTES[attribute_name][1])
    flight_duration = []
    for flight_elements in flight:
        if not flight_elements:
            flight_duration.append(None)
            continue
        duration_elements = flight_elements.text.split(':')[1].split()
        # if duration_elements[1][0] != 'h':
        #     hours = 0
        #     minutes = int(duration_elements[0])
        # elif len(duration_elements) < 3:
        #     hours = int(duration_elements[0])
        #     minutes = 0
        # else:
        #     hours = int(duration_elements[0])
        #     minutes = int(duration_elements[2])
        hours, minutes = time_components_checker(duration_elements)
        flight_duration.append(time(hours, minutes))  # what formate of time is better to store in database?
    return flight_duration


def get_stop_duration(flight):
    # flight = element.fildAll(ATTRIBUTES[attribute_name][0], class_=ATTRIBUTES[attribute_name][1])
    stop_duration = []
    for flight_elements in flight:
        if not flight_elements:
            stop_duration.append(None)
            continue
        stop_elements = flight_elements.text.split()
        # if stop_elements[1][0] != 'h':
        #     hours = 0
        #     minutes = int(stop_elements[0])
        # elif len(stop_elements) < 3:
        #     hours = int(stop_elements[0])
        #     minutes = 0
        # else:
        #     hours = int(stop_elements[0])
        #     minutes = int(stop_elements[2])
        hours, minutes = time_components_checker(stop_elements)
        stop_duration.append(time(hours, minutes))  # what formate of time is better to store in database?
    return stop_duration


def get_price(flight):
    # flight = element.fildAll(ATTRIBUTES[attribute_name][0], class_=ATTRIBUTES[attribute_name][1])
    price = None
    for flight_elements in flight:
        if flight_elements:
            price = flight_elements.text  # get integer!!
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


soup = main1(source)
li_elements = soup.findAll('li', class_=LI_CLASS_NAME)

li_string = [str(element).split() for element in li_elements]
flight_id_list = [li[4].split('"')[1] for li in li_string]  # indexes were checked manually on the site

for ind, li_element in enumerate(li_elements):

    departure_time, departure_airport = get_departure_arrival(get_element(li_element, 'Departure'))
    departure_info = {'Departure_hour': departure_time} | {'Departure_airport': departure_airport}
    # flight_departure = li_element.findAll(ATTRIBUTES['Departure'][0], class_=ATTRIBUTES['Departure'][1])
    # departure_time = {'Departure_hour': [time(int(d_time.text.split()[0].split(":")[0])
    #                                           if d_time.text.split()[2] == 'AM'
    #                                           else 12 + int(d_time.text.split()[0].split(":")[0]),
    #                                           int(d_time.text.split()[0].split(":")[1]))
    #                                      if d_time.text.split() else None
    #                                      for d_time in flight_departure]}
    # departure_airport = {'Departure_airport': [d_time.text.split()[-1].strip('()')
    #                                            if d_time.text.split() else None
    #                                            for d_time in flight_departure]}
    arrival_time, arrival_airport = get_departure_arrival(get_element(li_element, 'Arrival'))
    arrival_info = {'Arrival_hour': arrival_time} | {'Arrival_airport': arrival_airport}
    # flight_arrival = li_element.findAll(ATTRIBUTES['Arrival'][0], class_=ATTRIBUTES['Arrival'][1])
    # arrival_time = {'Arrival_hour': [time(int(a_time.text.split()[0].split(":")[0])
    #                                       if a_time.text.split()[2] == 'AM'
    #                                       else 12 + int(a_time.text.split()[0].split(":")[0]),
    #                                       int(a_time.text.split()[0].split(":")[1]))
    #                                  if a_time.text.split() else None
    #                                  for a_time in flight_arrival]}
    # arrival_airport = {'Arrival_airport': [a_time.text.split()[-1].strip('()')
    #                                        if a_time.text.split() else None
    #                                        for a_time in flight_arrival]}
    duration = get_flight_duration(get_element(li_element, 'Flight duration'))
    duration_info = {'Flight duration': duration}
    # flight_duration = li_element.findAll(ATTRIBUTES['Flight duration'][0], class_=ATTRIBUTES['Flight duration'][1])
    # duration = {'Flight duration': [time(int(f_duration.text.split(':')[1].split()[0]
    #                                      if f_duration.text.split(':')[1].split()[1] == 'hr' else 0),
    #                                      int(f_duration.text.split(':')[1].split()[0])
    #                                      if len(f_duration.text.split(':')[1].split()) < 3
    #                                      and f_duration.text.split(':')[1].split()[1] != 'hr'
    #                                      else (0 if len(f_duration.text.split(':')[1].split()) < 3
    #                                            else int(f_duration.text.split(':')[1].split()[2])))
    #                                 if f_duration.text.split(':') else None
    #                                 for f_duration in flight_duration]}
    # connection = get_stop_duration(get_element(li_element, 'Connection time'))
    # connection_info = {'Stop duration': connection}
    # flight_connection = li_element.findAll(ATTRIBUTES['Connection time'][0], class_=ATTRIBUTES['Connection time'][1])
    # connection = {'Connection_time': [time(int(f_connection.text.split()[0]),
    #                                        int(f_connection.text.split()[2]))
    #                                   if f_connection.text.split() else None
    #                                   for f_connection in flight_connection]}
    price = get_price(get_element(li_element, 'Price'))
    price_info = {'Price': price}
    # flight_price = li_element.findAll(ATTRIBUTES['Price'][0], class_=ATTRIBUTES['Price'][1])
    # price = {'Price': [f_price.text if f_price.text else None for f_price in flight_price][-1:]}
    co2_emission = get_co2_emission(get_element(li_element, 'CO2 emission'))
    co2_emission_info = {'CO2 emission': co2_emission}

    # flight_co2_emission = li_element.findAll(ATTRIBUTES['CO2 emission'][0], class_=ATTRIBUTES['CO2 emission'][1])
    # co2_emission = {'CO2 emission': [f_emission.text.split()[-2] if f_emission.text else None
    #                                  for f_emission in flight_co2_emission]}

    flight_facilities = li_element.findAll(ATTRIBUTES['Facilities'][0][0], class_=ATTRIBUTES['Facilities'][1][0])
    facilities = {'Facilities': [
        [facility.text for facility in
         f_facility.findAll(ATTRIBUTES['Facilities'][0][1], class_=ATTRIBUTES['Facilities'][1][1])
         if not facility.text[:6] == 'Carbon'] for f_facility in flight_facilities]}

    flights[flight_id_list[ind]] = (departure_info | arrival_info | duration_info |  price_info |
                                    co2_emission_info | facilities)  # connection_info |

for ind, flight in enumerate(flights.items()):
    print(ind, '\t', flight)
