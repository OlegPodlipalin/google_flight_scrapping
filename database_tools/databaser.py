import pymysql.cursors
from datetime import date
from libraries.get_from_library import get_data


class DatabaseCreateWrite:
    """ Class of the DB creator"""

    def __init__(self):
        self._data = get_data('databases')
        self.connection = pymysql.connect(host=self._data['host'],
                                          user=self._data['user'],
                                          password=self._data['password'],
                                          cursorclass=pymysql.cursors.DictCursor)

        self._trips_table = []
        self._flights_table = []
        self._new_airports = []
        self._new_facilities = []
        self._update_airports_table = []
        self._flight_facilities_table = []

        for query in self._data['execute_query']:
            self._execute_query(query)

        airports = self._read_from_table('airports')
        self._airports_table = {airport['iata_code']: (airport['id'], airport['name']) for airport in airports}
        facilities = self._read_from_table('facilities')
        self._facilities_table = {facility['text']: facility['id'] for facility in facilities}

        self._last_trip_number = self._get_last_id('trips', 'id') + 1
        self._last_flight_number = self._get_last_id('flights', 'id') + 1

        self._scrapping_date = date.today()

    def _read_from_table(self, table_name):
        with self.connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {table_name}")
        table = cursor.fetchall()
        return table

    def _get_last_id(self, table_name, id_arg):
        with self.connection.cursor() as cursor:
            cursor.execute(f"SELECT {id_arg} FROM {table_name} ORDER BY {id_arg} DESC LIMIT 1")
        last_id = cursor.fetchone()
        return 0 if last_id is None else last_id[id_arg]

    def _execute_query(self, query):
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            self.connection.commit()

    def _executemany_query(self, query, data):
        with self.connection.cursor() as cursor:
            cursor.executemany(query, data)
            self.connection.commit()

    def write_from_api(self, airports):
        for airport in airports:
            if self._airports_table.get(airport[0]) is None:
                self._airports_table[airport[0]] = (len(self._airports_table) + 1, airport[1])
                self._new_airports.append((airport[0], airport[1]))
            elif self._airports_table.get(airport[0])[1] == 'unknown':
                self._airports_table[airport[0]] = (self._airports_table[airport[0]][0], airport[1])
                self._update_airports_table.append(airport[0])

        for query, data in zip(self._data['executemany_query'][:2], [self._new_airports, self._update_airports_table]):
            self._executemany_query(query, data)

    def write_from_scrape(self, trips):
        for trip_unique_id, trip_details in trips.items():
            for flight_num_in_trip, flight_details in enumerate(zip(trip_details['Departure_airport'],
                                                                    trip_details['Arrival_airport'],
                                                                    trip_details['Departure_hour'],
                                                                    trip_details['Arrival_hour'],
                                                                    trip_details['Flight duration'],
                                                                    trip_details['CO2 emission'],
                                                                    trip_details['Facilities'])):

                for ind in [0, 1]:
                    if self._airports_table.get(flight_details[ind]) is None:
                        self._airports_table[flight_details[ind]] = (len(self._airports_table) + 1, 'unknown')
                        self._new_airports.append((flight_details[ind], 'unknown'))

                departure_airport_id = self._airports_table.get(flight_details[0])[0]
                arrival_airport_id = self._airports_table.get(flight_details[1])[0]

                flight_details_flight_table = [departure_airport_id, arrival_airport_id]
                flight_details_flight_table.extend(list(flight_details[2:-1]))
                flight_details_flight_table.extend([flight_num_in_trip, self._last_trip_number])
                self._flights_table.append(flight_details_flight_table)

                for facility in flight_details[-1]:
                    if self._facilities_table.get(facility) is None:
                        self._facilities_table[facility] = len(self._facilities_table) + 1
                        self._new_facilities.append(facility)
                    self._flight_facilities_table.append((self._last_flight_number,
                                                          self._facilities_table.get(facility)))
                self._last_flight_number += 1

            self._trips_table.append((trip_unique_id, self._scrapping_date, trip_details['Price']))
            self._last_trip_number += 1

        for query, data in zip(self._data['executemany_query'][1:], [self._update_airports_table,
                                                                     self._new_facilities,
                                                                     self._flight_facilities_table,
                                                                     self._flights_table,
                                                                     self._trips_table]):
            self._executemany_query(query, data)

    # def create_db(self):
    #     """Creates DB if it doesn't exist yet"""
    #     with self.connection.cursor() as cursor:
    #         # with self.cursor as cursor:
    #         cursor.execute(f"""CREATE DATABASE if not exists Google_flight""")
    #         self.connection.commit()
    #
    # def create_db_tables(self):
    #     """Create Tables in DB and Insert values into table facilities"""
    #     # connection = pymysql.connect(host='localhost',
    #     #                              user='root',
    #     #                              password='rootroot',
    #     #                              database='Google_flight',
    #     #                              cursorclass=pymysql.cursors.DictCursor)
    #     # connection.database()
    #     # cursor = connection.cursor()
    #
    #     # self.connection.database('Google_flight')
    #
    #     try:
    #         with self.connection.cursor() as cursor:
    #             cursor.execute("""USE Google_flight;""")
    #
    #             cursor.execute("""CREATE TABLE if not exists trips(
    #                               id INT PRIMARY KEY AUTO_INCREMENT,
    #                               unique_id VARCHAR(50),
    #                               date_of_scrape DATETIME,
    #                               price INT)""")
    #
    #             cursor.execute("""CREATE TABLE if not exists airports (
    #                               id INT PRIMARY KEY AUTO_INCREMENT,
    #                               abbreviation VARCHAR(50),
    #                               name VARCHAR(100),
    #                               city VARCHAR(50))""")
    #
    #             cursor.execute("""CREATE TABLE if not exists facilities(
    #                               id INT PRIMARY KEY AUTO_INCREMENT,
    #                               text VARCHAR(50))""")
    #
    #             cursor.execute("""CREATE TABLE if not exists flights(
    #                               id INT PRIMARY KEY AUTO_INCREMENT,
    #                               trip_id INT,
    #                               departure_time TIME,
    #                               departure_airport_id INT,
    #                               arrival_time TIME,
    #                               arrival_airport_id INT,
    #                               flight_duration TIME,
    #                               co2_emission VARCHAR(50),
    #                               flight_order_in_trip INT)
    #                               """)  # , FOREIGN KEY (trip_id) REFERENCES trips(id))
    #             # FOREIGN
    #             # KEY(departure_airport_id)
    #             # REFERENCES
    #             # airports(id),
    #             # FOREIGN
    #             # KEY(arrival_airport_id)
    #             # REFERENCES
    #             # airports(id))
    #
    #             cursor.execute("""CREATE TABLE if not exists flight_facilities (
    #                               flight_id INT,
    #                               facility_id INT)""")
    #             # FOREIGN
    #             # KEY(flight_id)
    #             # REFERENCES
    #             # flights(id),
    #             # FOREIGN
    #             # KEY(facility_id)
    #             # REFERENCES
    #             # facilities(id))
    #             self.connection.commit()
    #     except:
    #         print('Issue with table creation')
    #         pass


if __name__ == '__main__':
    pass
    # creator = Db_Creator()
    # creator.create_db()
    # creator.create_db_tables()
