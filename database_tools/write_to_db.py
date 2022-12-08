import pymysql.cursors
from datetime import date


class DBWriter:
    """ Class of the DB writer"""

    def __init__(self):
        # Constructor of the class
        self.connection = pymysql.connect(host='localhost',
                                          user='root',
                                          password='root',
                                          database='Google_flight',
                                          cursorclass=pymysql.cursors.DictCursor)
        self.facility_table = {}
        self.flight_facilities_table = []
        self.flight_table = []
        self.trip_table = []
        self.flight_num_for_facilities = 1  # get num from DB
        self.trip_number = 1  # get num from DB
        self.scrapping_date = date.today()

    # def write_from_api(self, airports):
    #     with self.connection.cursor() as cursor:
    #         cursor.executemany("""INSERT INTO flight_facilities (flight_id,facility_id)
    #                                              VALUES (%s, %s);""", self.flight_facilities_table)
    #         self.connection.commit()

    def write_facilities_to_db(self):
        """
        Write facilities details into DB Table facilities
        """
        with self.connection.cursor() as cursor:
            cursor.executemany("""INSERT INTO facilities (text)
                                    VALUES (%s);""", self.facility_table.keys())
            cursor.executemany("""INSERT INTO flight_facilities (flight_id,facility_id)
                                     VALUES (%s, %s);""", self.flight_facilities_table)
            self.connection.commit()

    def write_flight_to_db(self):
        """
        Write flight details into DB table flight
        """
        query = ("""INSERT INTO flights
                                     (departure_airport_id,departure_time,arrival_airport_id,arrival_time,flight_duration,co2_emission,flight_order_in_trip,trip_id)
                                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s);""")
        with self.connection.cursor() as cursor:
            cursor.executemany(query, self.flight_table)
            self.connection.commit()

    def write_trips_to_db(self):
        """
        Write trips details into DB Table trips
        """
        query = """INSERT INTO trips (unique_id,date_of_scrape,price)
                   VALUES (%s, %s, %s);"""

        # with self.connection as connection:
        with self.connection.cursor() as cursor:
            cursor.executemany(query, self.trip_table)
            self.connection.commit()

    def write_from_scrape(self, trips):
        for trip_unique_id, trip_details in trips.items():
            for flight_num_in_trip, flight_details in enumerate(zip(trip_details['Departure_airport'],
                                                                    trip_details['Departure_hour'],
                                                                    trip_details['Arrival_airport'],
                                                                    trip_details['Arrival_hour'],
                                                                    trip_details['Flight duration'],
                                                                    trip_details['CO2 emission'],
                                                                    trip_details['Facilities'])):
                flight_details_flight_table = list(flight_details[:-1])
                flight_details_flight_table.extend([flight_num_in_trip, self.trip_number])
                self.flight_table.append(flight_details_flight_table)

                for facility in flight_details[-1]:
                    if self.facility_table.get(facility) is None:
                        self.facility_table[facility] = len(self.facility_table) + 1
                    self.flight_facilities_table.append((self.flight_num_for_facilities,
                                                         self.facility_table.get(facility)))
                self.flight_num_for_facilities += 1

            self.trip_table.append((trip_unique_id, self.scrapping_date, trip_details['Price']))
            self.trip_number += 1

        self.write_facilities_to_db()
        self.write_flight_to_db()
        self.write_trips_to_db()


