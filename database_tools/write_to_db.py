import pymysql.cursors
from datetime import date


class DatabaseWriter:
    """ Class of the DB writer"""

    def __init__(self):
        # Constructor of the class
        self.connection = pymysql.connect(host='localhost',
                                          user='root',
                                          password='root',
                                          database='Google_flight',
                                          cursorclass=pymysql.cursors.DictCursor)

        self.flight_facilities_table = []
        self.flight_table = []
        self.trip_table = []
        self.new_airports = []
        self.new_facilities = []
        self.update_airports_table = []

        airports = self.read_from_table('airports')
        self.airports_table = {airport['abbreviation']: (airport['id'], airport['name']) for airport in airports}
        facilities = self.read_from_table('facilities')
        self.facilities_table = {facility['text']: facility['id'] for facility in facilities}

        self.last_flight_number = self.get_last_id('flights', 'id') + 1
        self.last_trip_number = self.get_last_id('trips', 'id') + 1

        self.scrapping_date = date.today()
        self.test = True

    def get_last_id(self, table_name, id_arg):
        with self.connection.cursor() as cursor:
            cursor.execute(f"SELECT {id_arg} FROM {table_name} ORDER BY {id_arg} DESC LIMIT 1")
        last_id = cursor.fetchone()
        return 0 if last_id is None else last_id[id_arg]

    def read_from_table(self, table_name):
        with self.connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {table_name}")
        table = cursor.fetchall()
        return table

    def update_airports_table(self, xxx):
        with self.connection.cursor() as cursor:
            cursor.executemany(f"UPDATE airports SET name = %s WHERE abbreviation = %s;", self.update_airports_table)
            self.connection.commit()

    def write_from_api(self, airports):
        for airport in airports:
            if self.airports_table.get(airport[0]) is None:
                self.airports_table[airport[0]] = (len(self.airports_table) + 1, airport[1])
                self.new_airports.append((airport[0], airport[1]))
            elif self.airports_table.get(airport[0])[1] == 'unknown':
                self.airports_table[airport[0]] = (self.airports_table[airport[0]][0], airport[1])
                self.update_airports_table.append(airport[0])

        query_write_airports = "INSERT INTO airports (abbreviation, name) VALUES (%s, %s);"

        with self.connection.cursor() as cursor:
            cursor.executemany(query_write_airports, [item for item in self.new_airports])
            self.connection.commit()

    def write_facilities_to_db(self):
        """
        Write facilities details into DB Table facilities
        """
        query_write_facilities = "INSERT INTO facilities (text) VALUES (%s);"
        query_write_flight_facilities = "INSERT INTO flight_facilities (flight_id, facility_id) VALUES (%s, %s);"
        with self.connection.cursor() as cursor:
            cursor.executemany(query_write_facilities, self.new_facilities)
            cursor.executemany(query_write_flight_facilities, self.flight_facilities_table)
            self.connection.commit()

    def write_flight_to_db(self):
        """
        Write flight details into DB table flight
        """
        query_write_flights = ("""INSERT INTO flights (departure_airport_id,
                                         arrival_airport_id,
                                         departure_time,
                                         arrival_time,
                                         flight_duration,
                                         co2_emission,
                                         flight_order_in_trip,
                                         trip_id)
                                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s);""")
        with self.connection.cursor() as cursor:
            if self.test:
                print(self.flight_table[0])
                self.test = False
            cursor.executemany(query_write_flights, self.flight_table)
            self.connection.commit()

    def write_trips_to_db(self):
        """
        Write trips details into DB Table trips
        """
        query_write_trips = "INSERT INTO trips (unique_id,date_of_scrape,price) VALUES (%s, %s, %s);"

        with self.connection.cursor() as cursor:
            cursor.executemany(query_write_trips, self.trip_table)
            self.connection.commit()

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
                    if self.airports_table.get(flight_details[ind]) is None:
                        self.airports_table[flight_details[ind]] = (len(self.airports_table) + 1, 'unknown')
                        self.new_airports.append((flight_details[ind], 'unknown'))

                departure_airport_id = self.airports_table.get(flight_details[0])[0]
                arrival_airport_id = self.airports_table.get(flight_details[1])[0]

                flight_details_flight_table = [departure_airport_id, arrival_airport_id]
                flight_details_flight_table.extend(list(flight_details[2:-1]))
                flight_details_flight_table.extend([flight_num_in_trip, self.last_trip_number])
                self.flight_table.append(flight_details_flight_table)

                for facility in flight_details[-1]:
                    if self.facilities_table.get(facility) is None:
                        self.facilities_table[facility] = len(self.facilities_table) + 1
                        self.new_facilities.append(facility)
                    self.flight_facilities_table.append((self.last_flight_number,
                                                         self.facilities_table.get(facility)))
                self.last_flight_number += 1

            self.trip_table.append((trip_unique_id, self.scrapping_date, trip_details['Price']))
            self.last_trip_number += 1

        self.write_facilities_to_db()
        self.write_flight_to_db()
        self.write_trips_to_db()


