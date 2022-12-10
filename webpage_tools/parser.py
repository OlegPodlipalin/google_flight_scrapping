import re
from datetime import datetime, date, time
from libraries.get_from_library import get_data

ATTRIB = {'Departure': ['div', 'dPzsIb AdWm1c y52p7d'],
          'Arrival': ['div', 'SWFQlc AdWm1c y52p7d'],
          'Flight duration': ['div', 'CQYfx y52p7d'],
          'Flight number': ['div', 'MX5RWe sSHqwe y52p7d'],
          # 'Connection time': ['div', 'tvtJdb eoY5cb y52p7d'],
          'Price': ['div', ['YMlIz FpEdX', 'YMlIz FpEdX jLMuyc']],
          'CO2 emission': ['span', 'gI4d6d'],
          'Facilities': ['ul', 'elO9Ce sSHqwe JNp8ff']}

# to be imported
LI_CLASS_NAME = 'pIav2d'


class GoogleFlightsParser:
    def __init__(self, soup):
        self.flights = dict()
        self._month_dict = get_data('months')
        self._today = date.today()
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

            flight_element_splited = flight_elements.get_text("##").split('##')
            n = (-3 if flight_element_splited[-1][0] == '(' else -2)
            hours_minutes = flight_element_splited[n].split()[0].split(':')
            am_pm = flight_element_splited[n].split()[1]
            airport = flight_element_splited[-1].strip('()')
            day = int(flight_element_splited[n].split()[-1])
            month = self._month_dict.get(flight_element_splited[n].split()[-2])
            year = self._today.year
            if self._today.month > month or (self._today.month == month and self._today.day >= day):
                year += 1

            if am_pm == 'PM' and hours_minutes[0] != '12':
                hours = int(hours_minutes[0]) + 12
            elif am_pm == 'AM' and hours_minutes[0] == '12':
                hours = 0
            else:
                hours = int(hours_minutes[0])
            minutes = int(hours_minutes[1])

            self._flight_time.append(datetime(year, month, day, hours, minutes))
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
            self._flight_duration.append(time(self._current_flight_hours,
                                              self._current_flight_minutes))  # what formate of time is better to store in database?

    def _get_flight_number(self, element_data, attribute_name):
        self._current_flight_data = element_data.findAll(ATTRIB[attribute_name][0], class_=ATTRIB[attribute_name][1])
        self._flight_number = []

        for flight_elements in self._current_flight_data:
            if not flight_elements:
                self._flight_number.append(None)
                continue
            self._flight_number.append(flight_elements.get_text("##").split('##')[-1])

    def _get_price(self, element_data, attribute_name):
        # self._get_element(element_data, attribute_name)
        self._current_flight_data = element_data.findAll(ATTRIB[attribute_name][0], class_=ATTRIB[attribute_name][1])
        self._price = None
        for flight_elements in self._current_flight_data:
            if flight_elements:
                self._price = int(re.sub(r'\D+', '', flight_elements.text))
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
        self._current_flight_data = element_data.findAll(ATTRIB[attrib_name][0], class_=ATTRIB[attrib_name][1])
        self._facilities = []
        for flight_elements in self._current_flight_data:
            self._facilities_list = flight_elements.get_text('##').split('##')
            for ind, facility in enumerate(self._facilities_list):
                if facility[:6] == 'Carbon':
                    self._facilities.append(self._facilities_list[:ind])
                    break

    def run(self):
        for li_element in self._li_elements:
            self._get_flight_id(li_element)

            self._get_departure_arrival(li_element, 'Departure')
            departure_info = {'Departure_hour': self._flight_time} | {'Departure_airport': self._flight_airport}

            self._get_departure_arrival(li_element, 'Arrival')
            arrival_info = {'Arrival_hour': self._flight_time} | {'Arrival_airport': self._flight_airport}

            self._get_flight_duration(li_element, 'Flight duration')
            duration_info = {'Flight_duration': self._flight_duration}

            self._get_flight_number(li_element, 'Flight number')
            number_info = {'Flight_number': self._flight_number}

            self._get_price(li_element, 'Price')
            price_info = {'Price': self._price}

            self._get_co2_emission(li_element, 'CO2 emission')
            co2_emission_info = {'CO2 emission': self._co2_emission}

            self._get_facilities(li_element, 'Facilities')
            facilities_info = {'Facilities': self._facilities}

            self.flights[self._current_flight_id] = departure_info | arrival_info | duration_info | number_info | \
                                                    price_info | co2_emission_info | facilities_info

# for ind, flight in enumerate(flights.items()):
#     print(ind, '\t', flight)
