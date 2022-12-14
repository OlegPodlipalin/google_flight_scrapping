import pymysql.cursors
from datetime import date

from pymysql import OperationalError, ProgrammingError
from tqdm import tqdm
from libraries.work_with_libraries import get_data, save_to_json
import logging


class DatabaseCreateWrite:
    """ Class of the DB creator"""

    def __init__(self):
        logging.info(f'DatabaseCreateWrite instance creation...')
        try:
            self._login = get_data('db_login')
        except FileNotFoundError:
            logging.info(f'Creating db_login.json library with users credentials for "mySQL" database')
            self._login = dict()
            print('Database access issue. File db_login is not found'
                  '\n\nProvide your credentials to access the database')
            logging.info(f'Getting credentials for database access from user')
            for key, message in zip(['host', 'user', 'password'], ['hostname', 'username', 'password']):
                self._login[key] = input(f'Enter your "mySQL" server {message}:\t')
            save_to_json('db_login', self._login)

        self._data = get_data('databases')
        # crushes when invalid credentials are provided!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        for _ in range(5):
            try:
                self._connection = pymysql.connect(host=self._login['host'],
                                                   user=self._login['user'],
                                                   password=self._login['password'],
                                                   cursorclass=pymysql.cursors.DictCursor)
                self._execute_query(f'SHOW DATABASES;')
            except OperationalError:
                print('Database access issue. Credentials are invalid'
                      '\n\nProvide your credentials to access the database')
                logging.info(f'Getting credentials for database access from user')
                for key, message in zip(['host', 'user', 'password'], ['hostname', 'username', 'password']):
                    self._login[key] = input(f'Enter your "mySQL" server {message}:\t')
                save_to_json('db_login', self._login)

        logging.info(f'Connection to database created')

        self._scrapping_date = date.today()
        self._destination = None
        self._trips_table = []
        self._new_flights = []
        self._new_airports = []
        self._new_facilities = []
        self._trips_flights_table = []
        self._update_airports_table = []
        self._flight_facilities_table = []
        self._airports_table = dict()
        self._facilities_table = dict()
        self._flights_table = dict()
        self._last_trip_number = None
        self._last_flight_number = None
        logging.info(f'DatabaseCreateWrite instance created')

        database = False
        try:
            logging.info(f'Checking to database to exist...')
            # crushes when invalid credentials are provided!!!!!!!!!!!!! maybe here
            self._execute_query(f'USE {self._data["database_name"]};')
            self._read_from_table('airports')
        except OperationalError:
            logging.info(f'Database does not exist. Creating database...')
            try:
                for query in self._data['execute_query']:
                    self._execute_query(query)
            except OperationalError:
                raise OperationalError('An issue with database creation.')
            else:
                database = True
        except ProgrammingError:
            logging.info(f'Database is empty. Creating tables...')
            try:
                for query in self._data['execute_query']:
                    self._execute_query(query)
            except OperationalError:
                raise OperationalError('An issue with tables creation.')
            else:
                database = True
        else:
            database = True

        if database:
            logging.info(f'Database ready to be used')
            airports = self._read_from_table('airports')
            self._airports_table = {airport['iata_code']: (airport['id'], airport['name']) for airport in airports}
            facilities = self._read_from_table('facilities')
            self._facilities_table = {facility['text']: facility['id'] for facility in facilities}
            flights = self._read_from_table('flights')
            self._flights_table = {flight['flight_num']: flight['id'] for flight in flights}

            self._last_trip_number = self._get_last_id('trips', 'id') + 1
            self._last_flight_number = self._get_last_id('flights', 'id') + 1

    def _read_from_table(self, table_name):
        logging.debug(f'Getting table {table_name}')
        with self._connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {table_name}")
        table = cursor.fetchall()
        logging.debug(f'Data form {table_name} extracted')
        return table

    def _get_last_id(self, table_name, id_arg):
        logging.debug(f'Getting last id from table {table_name}')
        with self._connection.cursor() as cursor:
            cursor.execute(f"SELECT {id_arg} FROM {table_name} ORDER BY {id_arg} DESC LIMIT 1")
        last_id = cursor.fetchone()
        logging.debug(f'Last id form {table_name} extracted')
        return 0 if last_id is None else last_id[id_arg]

    def _execute_query(self, query):
        logging.debug(f'Query {query} performing...')
        with self._connection.cursor() as cursor:
            cursor.execute(query)
            self._connection.commit()

    def _executemany_query(self, query, data):
        logging.debug(f'Query {query} performing...')
        with self._connection.cursor() as cursor:
            cursor.executemany(query, data)
            self._connection.commit()

    def write_from_api(self, airports):
        logging.info(f'Extracting data from API')
        for airport in airports:
            if self._airports_table.get(airport[0]) is None:
                self._airports_table[airport[0]] = (len(self._airports_table) + 1, airport[1])
                self._new_airports.append((airport[0], airport[1]))
            elif self._airports_table.get(airport[0])[1] == 'unknown':
                self._airports_table[airport[0]] = (self._airports_table[airport[0]][0], airport[1])
                self._update_airports_table.append(airport[0])
        logging.info(f'{len(self._new_airports)} new, {len(self._update_airports_table)} to update airports found.')

        logging.info(f'Writing/updating airports in database')
        for query, data in zip(self._data['executemany_query'][:2], [self._new_airports, self._update_airports_table]):
            self._executemany_query(query, data)

        self._new_airports = []
        self._update_airports_table = []

    def write_from_scrape(self, trips):
        self._destination = trips['destination']
        del trips['destination']
        logging.info(f'Extracting data from scraping before writing to database')
        bar = tqdm(desc=f'{self._destination} writing', total=len(trips))
        for trip_unique_id, trip_details in trips.items():
            logging.debug(f'Extracting data from trip {trip_unique_id}')
            for flight_num_in_trip, flight_details in enumerate(zip(trip_details['Departure_airport'],
                                                                    trip_details['Arrival_airport'],
                                                                    trip_details['Flight_number'],
                                                                    trip_details['Departure_hour'],
                                                                    trip_details['Arrival_hour'],
                                                                    trip_details['Flight_duration'],
                                                                    trip_details['CO2 emission'],
                                                                    trip_details['Facilities'])):

                if self._flights_table.get(flight_details[2]) is None:
                    self._flights_table[flight_details[2]] = len(self._flights_table) + 1
                    logging.debug(f'New flight {flight_details[2]} found')

                    for ind in [0, 1]:
                        if self._airports_table.get(flight_details[ind]) is None:
                            self._airports_table[flight_details[ind]] = (len(self._airports_table) + 1, 'unknown')
                            self._new_airports.append((flight_details[ind], 'unknown'))
                            logging.debug(f'New airport {flight_details[ind]} found')

                    departure_airport_id = self._airports_table.get(flight_details[0])[0]
                    arrival_airport_id = self._airports_table.get(flight_details[1])[0]

                    flight_details_flight_table = [departure_airport_id, arrival_airport_id]
                    flight_details_flight_table.extend(list(flight_details[2:-1]))
                    self._new_flights.append(flight_details_flight_table)

                    for facility in flight_details[-1]:
                        if self._facilities_table.get(facility) is None:
                            self._facilities_table[facility] = len(self._facilities_table) + 1
                            self._new_facilities.append(facility)
                            logging.debug(f'New facility {facility} found')
                        self._flight_facilities_table.append((self._flights_table.get(flight_details[2]),
                                                              self._facilities_table.get(facility)))

                self._trips_flights_table.append((self._last_trip_number,
                                                  self._flights_table.get(flight_details[2]),
                                                  flight_num_in_trip))

            self._trips_table.append((trip_unique_id, self._scrapping_date, trip_details['Price'], self._destination))
            self._last_trip_number += 1
            bar.update(1)

        logging.info(f'{len(self._new_airports)} new, {len(self._update_airports_table)} to update airports found.')
        logging.info(f'{len(self._new_flights)} new flights found.')
        logging.info(f'{len(self._new_facilities)} new facilities found.')
        logging.info(f'Writing data from scraping in database')
        for query, data in zip(self._data['executemany_query'], [self._new_airports,
                                                                 self._update_airports_table,
                                                                 self._new_facilities,
                                                                 self._flight_facilities_table,
                                                                 self._new_flights,
                                                                 self._trips_flights_table,
                                                                 self._trips_table]):
            self._executemany_query(query, data)

        self._trips_table = []
        self._new_flights = []
        self._new_airports = []
        self._new_facilities = []
        self._trips_flights_table = []
        self._update_airports_table = []
        self._flight_facilities_table = []


if __name__ == '__main__':
    pass
    # creator = Db_Creator()
    # creator.create_db()
    # creator.create_db_tables()
