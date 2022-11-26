from datetime import time

DESTINATIONS = {1: 'PAR',
                2: 'BER',
                3: 'AMS',
                4: 'ROM',
                5: 'MAD'}

CHOOSE_YOUR_OPTION = 2  # 1 - Paris, 2 - Berlin, 3 - Amsterdam, 4 - Roma, 5 -Madrid
# CHOOSE_YOUR_OPTION_DAY = not ready yet. the same as with CHOOSE_YOUR_OPTION (destination)

ATTRIB = {'Departure': ['div', 'dPzsIb AdWm1c y52p7d'],
          'Arrival': ['div', 'SWFQlc AdWm1c y52p7d'],
          'Flight duration': ['div', 'CQYfx y52p7d'],
          # 'Connection time': ['div', 'tvtJdb eoY5cb y52p7d'],
          'Price': ['div', ['YMlIz FpEdX', 'YMlIz FpEdX jLMuyc']],
          'CO2 emission': ['span', 'gI4d6d'],
          'Facilities': [['ul', 'li'], ['elO9Ce sSHqwe JNp8ff', 'WtSsrd']]}

# {'Company': 'Xsgmwe', 'Flight number': 'Xsgmwe QS0io', 'Type of flight': 'J2OpGd sSHqwe'} hard to scrape

SCRAPPED_PARAMETERS = {"dept_time": "dPzsIb AdWm1c y52p7d"}

# to be imported
LI_CLASS_NAME = 'pIav2d'
# flights = dict()
# source to be imported
source = f'https://www.google.com/travel/flights?q=Flights%20to%20{DESTINATIONS[CHOOSE_YOUR_OPTION]}%20from%20TLV%20on%202022-12-20%20through%202022-12-30%20one-way&curr=EUR'


class GoogleFlightsParser:
    def __init__(self, soup):
        self.flights = dict()
        self._li_elements = soup.findAll('li', class_=LI_CLASS_NAME)
        self.run()

    def _get_flight_id(self, element_data):
        element_data_string = str(element_data).split()
        # li_string = [str(element).split() for element in self._li_elements]
        self._current_flight_id = element_data_string[4].split('"')[1]  # indexes were checked manually on the site

    def _get_departure_arrival(self, element_data, attribute_name):
        # self._get_element(element_data, attribute_name)
        self._current_flight_data = element_data.findAll(ATTRIB[attribute_name][0], class_=ATTRIB[attribute_name][1])
        self._flight_time = []
        self._flight_airport = []

        for flight_elements in self._current_flight_data:
            if not flight_elements:
                self._flight_time.append(None)
                self._flight_airport.append(None)
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

            self._flight_time.append(time(hours, minutes))  # what formate of time is better to store in database?
            self._flight_airport.append(airport)

    def _time_components_checker(self, elements):
        if elements[1][0] != 'h':
            self._current_flight_hours = 0
            self._current_flight_minutes = int(elements[0])
        elif len(elements) < 3:
            self._current_flight_hours = int(elements[0])
            self._current_flight_minutes = 0
        else:
            self._current_flight_hours = int(elements[0])
            self._current_flight_minutes = int(elements[2])

    def _get_flight_duration(self, element_data, attribute_name):
        # self._get_element(element_data, attribute_name)
        self._current_flight_data = element_data.findAll(ATTRIB[attribute_name][0], class_=ATTRIB[attribute_name][1])
        self._flight_duration = []

        for flight_elements in self._current_flight_data:
            if not flight_elements:
                self._flight_duration.append(None)
                continue
            duration_elements = flight_elements.text.split(':')[1].split()
            self._time_components_checker(duration_elements)
            self._flight_duration.append(time(self._current_flight_hours, self._current_flight_minutes))  # what formate of time is better to store in database?

    # def get_stop_duration(flight):
    #     stop_duration = []
    #     for flight_elements in flight:
    #         if not flight_elements:
    #             stop_duration.append(None)
    #             continue
    #         stop_elements = flight_elements.text.split()
    #         hours, minutes = time_components_checker(stop_elements)
    #         stop_duration.append(time(hours, minutes))  # what formate of time is better to store in database?
    #     return stop_duration

    def _get_price(self, element_data, attribute_name):
        # self._get_element(element_data, attribute_name)
        self._current_flight_data = element_data.findAll(ATTRIB[attribute_name][0], class_=ATTRIB[attribute_name][1])
        self._price = None
        for flight_elements in self._current_flight_data:
            if flight_elements:
                self._price = flight_elements.text  # TODO get integer!!
                break

    def _get_co2_emission(self, element_data, attribute_name):
        # self._get_element(element_data, attribute_name)
        self._current_flight_data = element_data.findAll(ATTRIB[attribute_name][0], class_=ATTRIB[attribute_name][1])
        self._co2_emission = []
        for flight_elements in self._current_flight_data:
            if not flight_elements:
                self._co2_emission.append(None)
                continue
            self._co2_emission.append(flight_elements.text.split()[-2])

    def _get_facilities(self, element_data, attrib_name):
        self._current_flight_data = element_data.findAll(ATTRIB[attrib_name][0][0], class_=ATTRIB[attrib_name][1][0])
        self._facilities = []
        for flight_elements in self._current_flight_data:
            self._facilities_list = flight_elements.findAll(ATTRIB[attrib_name][0][1], class_=ATTRIB[attrib_name][1][1])
            self._facilities.append([facility.text for facility in self._facilities_list
                                     if not facility.text[:6] == 'Carbon'])

    def run(self):
        for li_element in self._li_elements:
            self._get_flight_id(li_element)

            self._get_departure_arrival(li_element, 'Departure')
            departure_info = {'Departure_hour': self._flight_time} | {'Departure_airport': self._flight_airport}

            self._get_departure_arrival(li_element, 'Arrival')
            arrival_info = {'Arrival_hour': self._flight_time} | {'Arrival_airport': self._flight_airport}

            self._get_flight_duration(li_element, 'Flight duration')
            duration_info = {'Flight duration': self._flight_duration}  # TODO: check bugs here

            # connection = get_stop_duration(get_element(li_element, 'Connection time'))
            # connection_info = {'Stop duration': connection}

            self._get_price(li_element, 'Price')
            price_info = {'Price': self._price}

            self._get_co2_emission(li_element, 'CO2 emission')
            co2_emission_info = {'CO2 emission': self._co2_emission}

            self._get_facilities(li_element, 'Facilities')
            facilities_info = {'Facilities': self._facilities}

            self.flights[self._current_flight_id] = \
                departure_info | arrival_info | duration_info | price_info | co2_emission_info | facilities_info
            # | connection_info

# for ind, flight in enumerate(flights.items()):
#     print(ind, '\t', flight)
