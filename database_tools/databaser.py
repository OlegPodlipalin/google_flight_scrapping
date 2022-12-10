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
        self._new_flights = []
        self._new_airports = []
        self._new_facilities = []
        self._trips_flights_table = []
        self._update_airports_table = []
        self._flight_facilities_table = []

        for query in self._data['execute_query']:
            self._execute_query(query)

        airports = self._read_from_table('airports')
        self._airports_table = {airport['iata_code']: (airport['id'], airport['name']) for airport in airports}
        facilities = self._read_from_table('facilities')
        self._facilities_table = {facility['text']: facility['id'] for facility in facilities}
        flights = self._read_from_table('flights')
        self._flights_table = {flight['flight_num']: flight['id'] for flight in flights}

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

        self._new_airports = []
        self._update_airports_table = []

    def write_from_scrape(self, trips):
        for trip_unique_id, trip_details in trips.items():
            for flight_num_in_trip, flight_details in enumerate(zip(trip_details['Departure_airport'],
                                                                    trip_details['Arrival_airport'],
                                                                    trip_details['Flight_number'],
                                                                    trip_details['Departure_hour'],
                                                                    trip_details['Arrival_hour'],
                                                                    trip_details['Flight_duration'],
                                                                    trip_details['CO2 emission'],
                                                                    trip_details['Facilities'])):

                """for airport in airports:
                    if self._airports_table.get(airport[0]) is None:
                        self._airports_table[airport[0]] = (len(self._airports_table) + 1, airport[1])
                        self._new_airports.append((airport[0], airport[1]))
                    elif self._airports_table.get(airport[0])[1] == 'unknown':
                        self._airports_table[airport[0]] = (self._airports_table[airport[0]][0], airport[1])
                        self._update_airports_table.append(airport[0])"""

                """ for facility in flight_details[-1]:
                    if self._facilities_table.get(facility) is None:
                        self._facilities_table[facility] = len(self._facilities_table) + 1
                        self._new_facilities.append(facility)
                    self._flight_facilities_table.append((self._last_flight_number,
                                                          self._facilities_table.get(facility)))
                self._last_flight_number += 1"""
                if self._flights_table.get(flight_details[2]) is None:
                    self._flights_table[flight_details[2]] = len(self._flights_table) + 1

                    # self._new_flights.append(flight_details[2])

                    for ind in [0, 1]:
                        if self._airports_table.get(flight_details[ind]) is None:
                            self._airports_table[flight_details[ind]] = (len(self._airports_table) + 1, 'unknown')
                            self._new_airports.append((flight_details[ind], 'unknown'))

                    departure_airport_id = self._airports_table.get(flight_details[0])[0]
                    arrival_airport_id = self._airports_table.get(flight_details[1])[0]

                    flight_details_flight_table = [departure_airport_id, arrival_airport_id]
                    flight_details_flight_table.extend(list(flight_details[2:-1]))
                    # flight_details_flight_table.extend([flight_num_in_trip, self._last_trip_number])
                    self._new_flights.append(flight_details_flight_table)

                    for facility in flight_details[-1]:
                        if self._facilities_table.get(facility) is None:
                            self._facilities_table[facility] = len(self._facilities_table) + 1
                            self._new_facilities.append(facility)
                        self._flight_facilities_table.append((self._flights_table.get(flight_details[2]),
                                                              self._facilities_table.get(facility)))

                self._trips_flights_table.append((self._last_trip_number,
                                                  self._flights_table.get(flight_details[2]),
                                                  flight_num_in_trip))

            self._trips_table.append((trip_unique_id, self._scrapping_date, trip_details['Price']))
            self._last_trip_number += 1

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
