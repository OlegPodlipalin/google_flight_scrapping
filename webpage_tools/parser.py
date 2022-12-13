import re
import logging
from tqdm import tqdm
from datetime import datetime, date, time
from libraries.get_from_library import get_data


class GoogleFlightsParser:
    def __init__(self, soup):
        logging.info('GoogleFlightsParser instance creation...')
        self._data = get_data('scraping_parsing')
        self._month_dict = get_data('months')
        self._today = date.today()
        self._li_elements = soup[0].findAll('li', class_=self._data['li_class_name'])
        self._webpage = soup[1]
        self._destination = soup[2]

        self.trips = dict()
        self._price = None
        self._current_trip_id = None
        self._facilities = []
        self._flight_time = []
        self._co2_emission = []
        self._flight_number = []
        self._flight_airport = []
        self._flight_duration = []
        logging.info('GoogleFlightsParser instance created')

        self.run()

    def _get_trip_id(self, element_data):
        logging.debug(f'Getting "Trip id" for {self._destination}')
        element_data_string = str(element_data).split()
        # li_string = [str(element).split() for element in self._li_elements]
        self._current_trip_id = element_data_string[4].split('"')[1]  # indexes were checked manually on the site

    def _get_departure_arrival(self, element_data, attribute_name):
        logging.debug(f'Getting "{attribute_name}" for {self._destination}')
        current_trip_data = element_data.findAll(self._data[attribute_name][0], class_=self._data[attribute_name][1])

        for flight_elements in current_trip_data:
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

    def _get_flight_duration(self, element_data, attribute_name):
        logging.debug(f'Getting "{attribute_name}" for {self._destination}')
        current_trip_data = element_data.findAll(self._data[attribute_name][0], class_=self._data[attribute_name][1])

        for flight_elements in current_trip_data:
            if not flight_elements:
                self._flight_duration.append(None)
                continue
            duration_elements = flight_elements.text.split(':')[1].split()

            if duration_elements[1][0] != 'h':
                current_flight_hours = 0
                current_flight_minutes = int(duration_elements[0])
            elif len(duration_elements) < 3:
                current_flight_hours = int(duration_elements[0])
                current_flight_minutes = 0
            else:
                current_flight_hours = int(duration_elements[0])
                current_flight_minutes = int(duration_elements[2])

            self._flight_duration.append(time(current_flight_hours, current_flight_minutes))

    def _get_flight_number(self, element_data, attribute_name):
        logging.debug(f'Getting "{attribute_name}" for {self._destination}')
        current_trip_data = element_data.findAll(self._data[attribute_name][0], class_=self._data[attribute_name][1])

        for flight_elements in current_trip_data:
            if not flight_elements:
                self._flight_number.append(None)
                continue
            self._flight_number.append(flight_elements.get_text("##").split('##')[-1])

    def _get_price(self, element_data, attribute_name):
        logging.debug(f'Getting "{attribute_name}" for {self._destination}')
        current_trip_data = element_data.findAll(self._data[attribute_name][0], class_=self._data[attribute_name][1])
        for flight_elements in current_trip_data:
            if flight_elements:
                self._price = int(re.sub(r'\D+', '', flight_elements.text))
                break

    def _get_co2_emission(self, element_data, attribute_name):
        logging.debug(f'Getting "{attribute_name}" for {self._destination}')
        current_trip_data = element_data.findAll(self._data[attribute_name][0], class_=self._data[attribute_name][1])

        for flight_elements in current_trip_data:
            if not flight_elements:
                self._co2_emission.append(None)
                continue
            self._co2_emission.append(flight_elements.text.split()[-2])

    def _get_facilities(self, element_data, attribute_name):
        logging.debug(f'Getting "{attribute_name}" for {self._destination}')
        current_trip_data = element_data.findAll(self._data[attribute_name][0], class_=self._data[attribute_name][1])

        for flight_elements in current_trip_data:
            facilities_list = flight_elements.get_text('##').split('##')
            for ind, facility in enumerate(facilities_list):
                if facility[:6] == 'Carbon':
                    self._facilities.append(facilities_list[:ind])
                    break

    def run(self):
        logging.info(f'Start parsing {self._webpage}')
        number_elements = len(self._li_elements)
        bar = tqdm(desc=f'{self._destination} parsing', total=number_elements)
        for n, li_element in enumerate(self._li_elements):
            logging.debug(f'Parsing element {n}/{number_elements} from {self._webpage}')
            self._get_trip_id(li_element)

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

            logging.debug(f'All parameters for element {n}/{number_elements} from {self._webpage} received')
            self.trips[self._current_trip_id] = departure_info | arrival_info | duration_info | number_info | \
                                                price_info | co2_emission_info | facilities_info

            self._price = None
            self._current_trip_id = None
            self._facilities = []
            self._flight_time = []
            self._co2_emission = []
            self._flight_number = []
            self._flight_airport = []
            self._flight_duration = []

            bar.update(1)
        self.trips['destination'] = self._destination
        logging.info(f'All elements form {self._webpage} parsed')
