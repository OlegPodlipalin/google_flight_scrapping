import re
import logging
from tqdm import tqdm
from datetime import datetime, date, time
from libraries.work_with_libraries import get_data


class GoogleFlightsParser:
    def __init__(self, soup):
        """
        Creates a new GoogleFlightsParser object. Takes in a BeautifulSoup object and full description of a current
        webpage and short description of a destination. Process the BeautifulSoup object using different html objects
        and their class names from scraping_parsing.json library file. Collects data in .trips parameter in nested
        dictionary.
        \nExample:
        {trip_code_1: {Departure_hour: [datetime, ...], Departure_airport: [str, ...], Arrival_hour:
        [datetime,...], Arrival_airport: [str, ...], Flight_duration: [time, ...], Flight_number: [str, ...],
        Price: int, CO2 emission: [str, ...], Facilities: [[str, ...], [str, ...], ...]}, trip_code_2: {...}, ...}\n
        :param soup: a tuple containing a BeautifulSoup object, full description of a webpage it was scraped from and a
        short description of a destination (BeautifulSoup, str, str)
        """
        logging.info('GoogleFlightsParser instance creation...')
        # getting data from scraping_parsing.json and months.json libraries
        self._data = get_data('scraping_parsing')
        self._month_dict = get_data('months')
        # getting date of scraping
        self._today = date.today()
        # getting list of individual trips from BeautifulSoup object.
        self._li_elements = soup[0].findAll('li', class_=self._data['li_class_name'])
        # saving destination information
        self._webpage = soup[1]
        self._destination = soup[2]

        # instance parameters initialization
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

        self._run()

    def _get_trip_id(self, element_data):
        logging.debug(f'Getting "Trip id" for {self._destination}')
        element_data_string = str(element_data).split()
        # li_string = [str(element).split() for element in self._li_elements]
        self._current_trip_id = element_data_string[4].split('"')[1]  # indexes were checked manually on the site

    def _get_departure_arrival(self, element_data, attribute_name):
        """
        Private method for getting the departure and arrival information from an element. Stores the data in
        ._flight_time and ._flight_airport containers
        :param element_data: a BeautifulSoup object contains data about individual trip
        :param attribute_name: name of data parameter to be parsed. Represent a key for scraping_parsing library to
        find html object type name and its class name parameter.
        """
        logging.debug(f'Getting "{attribute_name}" for {self._destination}')
        # extracting arrival and departure data for individual flights inside a trip
        current_trip_data = element_data.findAll(self._data[attribute_name][0], class_=self._data[attribute_name][1])

        self._flight_time = []
        self._flight_airport = []

        for flight_elements in current_trip_data:
            # parsing information about one flight
            if not flight_elements:
                self._flight_time.append(None)
                self._flight_airport.append(None)
                continue

            # splitting html object content into individual text objects
            flight_element_splited = flight_elements.get_text("##").split('##')
            # finding an appropriate text element index. using negative indexing in order to tackle an issue with
            # different elements number and more complex ascending indexing (more than 2 options for required element)
            n = (-3 if flight_element_splited[-1][0] == '(' else -2)
            hours_minutes = flight_element_splited[n].split()[0].split(':')
            am_pm = flight_element_splited[n].split()[1]
            airport = flight_element_splited[-1].strip('()')
            day = int(flight_element_splited[n].split()[-1])
            # encoding str representation of month using "months.json" library
            month = self._month_dict.get(flight_element_splited[n].split()[-2])
            year = self._today.year
            if self._today.month > month or (self._today.month == month and self._today.day >= day):
                # if the date of request < today - assign to 'year' 'next year' value
                year += 1

            # encoding 12-hours format to 24-hours
            if am_pm == 'PM' and hours_minutes[0] != '12':
                hours = int(hours_minutes[0]) + 12
            elif am_pm == 'AM' and hours_minutes[0] == '12':
                hours = 0
            else:
                hours = int(hours_minutes[0])
            minutes = int(hours_minutes[1])

            # filling trip containers with flight information. flight time in datetime.datetime format
            self._flight_time.append((date(year, month, day), time(hours, minutes)))
            self._flight_airport.append(airport)

    def _get_flight_duration(self, element_data, attribute_name):
        """
        Private method for getting flight duration information from an element. Stores the data in
        ._flight_duration container
        :param element_data: a BeautifulSoup object contains data about individual trip
        :param attribute_name: name of data parameter to be parsed. Represent a key for scraping_parsing library to
        find html object type name and its class name parameter.
        """
        logging.debug(f'Getting "{attribute_name}" for {self._destination}')
        # extracting flight duration data for individual flights inside a trip
        current_trip_data = element_data.findAll(self._data[attribute_name][0], class_=self._data[attribute_name][1])

        for flight_elements in current_trip_data:
            # parsing information about one flight
            if not flight_elements:
                self._flight_duration.append(None)
                continue
            # splitting html object content into individual text objects
            duration_elements = flight_elements.text.split(':')[1].split()

            # processing flight duration data
            if duration_elements[1][0] != 'h':
                # in this case flight duration less than one hour
                current_flight_hours = 0
                current_flight_minutes = int(duration_elements[0])
            elif len(duration_elements) < 3:
                # in this case flight duration presented only by hours
                current_flight_hours = int(duration_elements[0])
                current_flight_minutes = 0
            else:
                # regular case when both hours and minutes presented
                current_flight_hours = int(duration_elements[0])
                current_flight_minutes = int(duration_elements[2])

            # filling trip container with flight duration data in datetime.time format
            self._flight_duration.append(time(current_flight_hours, current_flight_minutes))

    def _get_flight_number(self, element_data, attribute_name):
        """
        Private method for getting flight number information from an element. Stores the data in
        ._flight_number container
        :param element_data: a BeautifulSoup object contains data about individual trip
        :param attribute_name: name of data parameter to be parsed. Represent a key for scraping_parsing library to
        find html object type name and its class name parameter.
        """
        logging.debug(f'Getting "{attribute_name}" for {self._destination}')
        # extracting flight number data for individual flights inside a trip
        current_trip_data = element_data.findAll(self._data[attribute_name][0], class_=self._data[attribute_name][1])

        for flight_elements in current_trip_data:
            # parsing information about one flight
            if not flight_elements:
                self._flight_number.append(None)
                continue
            # splitting html object content into individual text objects. Filling relevant data in trip container
            self._flight_number.append(flight_elements.get_text("##").split('##')[-1])

    def _get_price(self, element_data, attribute_name):
        """
        Private method for getting trip price information from an element. Stores the data in
        ._price container
        :param element_data: a BeautifulSoup object contains data about individual trip
        :param attribute_name: name of data parameter to be parsed. Represent a key for scraping_parsing library to
        find html object type name and its class name parameter.
        """
        logging.debug(f'Getting "{attribute_name}" for {self._destination}')
        # extracting trip price data for individual flights inside a trip
        current_trip_data = element_data.findAll(self._data[attribute_name][0], class_=self._data[attribute_name][1])
        for flight_elements in current_trip_data:
            # there are several text options with the same information
            if flight_elements:
                self._price = int(re.sub(r'\D+', '', flight_elements.text))
                # after finding and storing data in a trip container algorithm breaks the loop
                break

    def _get_co2_emission(self, element_data, attribute_name):
        """
        Private method for getting flight CO2 emission information from an element. Stores the data in
        ._co2_emission container
        :param element_data: a BeautifulSoup object contains data about individual trip
        :param attribute_name: name of data parameter to be parsed. Represent a key for scraping_parsing library to
        find html object type name and its class name parameter.
        """
        logging.debug(f'Getting "{attribute_name}" for {self._destination}')
        # extracting flight co2 emission data for individual flights inside a trip
        current_trip_data = element_data.findAll(self._data[attribute_name][0], class_=self._data[attribute_name][1])

        for flight_elements in current_trip_data:
            # parsing information about one flight
            if not flight_elements:
                self._co2_emission.append(None)
                continue
            # splitting html object content into individual text objects. Filling relevant data in trip container
            self._co2_emission.append(flight_elements.text.split()[-2])

    def _get_facilities(self, element_data, attribute_name):
        """
        Private method for getting flight facilities information from an element. Stores the data in
        ._co2_emission container
        :param element_data: a BeautifulSoup object contains data about individual trip
        :param attribute_name: name of data parameter to be parsed. Represent a key for scraping_parsing library to
        find html object type name and its class name parameter.
        """
        logging.debug(f'Getting "{attribute_name}" for {self._destination}')
        # extracting flight facilities data for individual flights inside a trip
        current_trip_data = element_data.findAll(self._data[attribute_name][0], class_=self._data[attribute_name][1])

        for flight_elements in current_trip_data:
            # parsing information about one flight
            facilities_list = flight_elements.get_text('##').split('##')
            for ind, facility in enumerate(facilities_list):
                # every flight contains a list of facilities. going through each facility
                if facility[:6] == 'Carbon':
                    # all the facilities appear before "carbon emission..." information
                    # append all the facilities elements using list slicing. Filling trip container with data
                    self._facilities.append(facilities_list[:ind])
                    break

    def _run(self):
        """
        Private method to data parsing algorithm start. Parse BeautifulSoup objects
        """
        logging.info(f'Start parsing {self._webpage}')
        number_elements = len(self._li_elements)
        bar = tqdm(desc=f'{self._destination} parsing', total=number_elements)
        # processing all trip elements
        for n, li_element in enumerate(self._li_elements):
            logging.debug(f'Parsing element {n}/{number_elements} from {self._webpage}')
            # getting and storing departure and arrival data from element (uses the same function and variable)
            self._get_departure_arrival(li_element, 'Departure')
            departure_info = {'Departure_hour': self._flight_time} | {'Departure_airport': self._flight_airport}
            self._get_departure_arrival(li_element, 'Arrival')
            arrival_info = {'Arrival_hour': self._flight_time} | {'Arrival_airport': self._flight_airport}

            # getting all the rest data from element
            self._get_flight_duration(li_element, 'Flight duration')
            self._get_flight_number(li_element, 'Flight number')
            self._get_price(li_element, 'Price')
            self._get_co2_emission(li_element, 'CO2 emission')
            self._get_facilities(li_element, 'Facilities')
            self._get_trip_id(li_element)

            # storing all the rest data from
            duration_info = {'Flight_duration': self._flight_duration}
            number_info = {'Flight_number': self._flight_number}
            price_info = {'Price': self._price}
            co2_emission_info = {'CO2 emission': self._co2_emission}
            facilities_info = {'Facilities': self._facilities}

            logging.debug(f'All parameters for element {n}/{number_elements} from {self._webpage} received')
            # saving all the data from element in .trips parameter
            self.trips[self._current_trip_id] = departure_info | arrival_info | duration_info | number_info | \
                                                price_info | co2_emission_info | facilities_info

            # cleaning containers before processing next element
            self._price = None
            self._current_trip_id = None
            self._facilities = []
            self._flight_time = []
            self._co2_emission = []
            self._flight_number = []
            self._flight_airport = []
            self._flight_duration = []

            bar.update(1)
        # adding short description of a destination to .trips parameter
        self.trips['destination'] = self._destination
        logging.info(f'All elements form {self._webpage} parsed')
