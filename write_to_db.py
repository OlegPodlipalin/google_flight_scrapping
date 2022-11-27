from bs4 import BeautifulSoup
import pymysql.cursors
from datetime import date, datetime
import main
import re
import datetime
from itertools import repeat

final_list =[]

def write_data_to_db(parser_flights):
    """
    Preliminary Parsing  from the website data
    """
    unique_ids = parser_flights.keys()
    flight_details = parser_flights.values()

    #initalizing list for each flight attribute
    flight_departure_airport = []
    flight_departure_hour = []
    flight_arrival_airport = []
    flight_arrival_hour = []
    flight_duration = []
    flight_price = []
    flight_co2_emission = []
    flight_facilities = []

    for flight in flight_details:
        # Appending each attributes to its own list
        flight_departure_airport.append(flight['Departure_airport'])
        flight_departure_hour.append(flight['Departure_hour'])

        flight_arrival_airport.append(flight['Arrival_airport'])
        flight_arrival_hour.append(flight['Arrival_hour'])

        flight_duration.append(flight['Flight duration'])
        flight_price.append(flight['Price'])

        flight_co2_emission.append(flight['CO2 emission'])
        flight_facilities.append(flight['Facilities'])

    # fix for the first flight price
    flight_price[0] = '0'
    #call for facilities_to_db
    write_facilities_to_db(flight_facilities)

    # call for trips_to_db
    write_trips_to_db(unique_ids,flight_price)

    # call for flights_to_db
    write_flight_to_db(flight_departure_airport, flight_departure_hour, flight_arrival_airport, flight_arrival_hour,
                         flight_duration, flight_co2_emission,flight_facilities)




# def query_for_flight_facilities(flight_id,facility_id):
# """
# Filling flight_facilities table
# """
#     query = """INSERT INTO flight_facilities (flight_id,facility_id)
#                                  VALUES (%s, %s);"""
#
#     connection = pymysql.connect(host='localhost',
#                                  user='root',
#                                  password='rootroot',
#                                  database='Google_flight',
#                                  cursorclass=pymysql.cursors.DictCursor)
#
#     datas = list(zip(repeat(flight_id),facility_id))
#
#     with connection.cursor() as cursor:
#         cursor.executemany(query,datas)
#         connection.commit()


def write_flight_to_db(flight_departure_airport,flight_departure_hour,flight_arrival_airport,flight_arrival_hour,flight_duration,flight_co2_emission,flight_facilities):
    """
    Write flight details into DB table flight
    """
    datas = []
    flight_counter = 1

    for i,data in enumerate(zip(flight_departure_airport,flight_departure_hour,flight_arrival_airport,flight_arrival_hour,flight_duration,flight_co2_emission,flight_facilities)):
        for j,element in enumerate(zip(data[0],data[1],data[2],data[3],data[4],data[5],data[6])):
            element = list(element)
            #query_for_flight_facilities(flight_counter,link_facility_to_flight(element[-1]))
            element.extend([j,i])
            datas.append(element)


    query = ("""INSERT INTO flights
                                 (departure_airport_id,departure_time,arrival_airport_id,arrival_time,flight_duration,co2_emission,flight_order_in_trip,trip_id)
                                 VALUES (%s, %s, %s,%s, %s, %s,%s,%s);""")

    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='rootroot',
                                 database='Google_flight',
                                 cursorclass=pymysql.cursors.DictCursor)

    with connection.cursor() as cursor:
        cursor.executemany(query, datas)
        connection.commit()


def link_facility_to_flight(flight_facilities):
    """
    Link facility to flight
    """
    for i,facility in enumerate(flight_facilities):
        flight_facilities[i]= final_list.index(facility)
    return flight_facilities





def write_trips_to_db(unique_ids,flight_price):
        """
        Write trips details into DB Table trips
        """
        datas = []
        scrapping_date = date.today()

        #erasing all euros signs from price flight and transforming values to integers

        for i,price in enumerate(flight_price):
            flight_price[i] = int(re.sub(r'\D+','',price))

        for i,id in enumerate(unique_ids):
            datas.append((id,scrapping_date,flight_price[i]))

        query = """INSERT INTO trips
                             (unique_id,date_of_scrape,price)
                             VALUES (%s, %s, %s);"""

        connection = pymysql.connect(host='localhost',
                                     user='root',
                                     password='rootroot',
                                     database='Google_flight',
                                     cursorclass=pymysql.cursors.DictCursor)

        with connection.cursor() as cursor:
            cursor.executemany(query, datas)
            connection.commit()




def write_facilities_to_db(flight_facilities):
    """
    Write facilities details into DB Table facilities
    """
    datas = set()
    for flight_elements in flight_facilities:
        for element in flight_elements:
            for facility in element:
                datas.add(facility)

    global final_list
    final_list = list(datas)

    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='rootroot',
                                 database='Google_flight',
                                 cursorclass=pymysql.cursors.DictCursor)

    with connection.cursor() as cursor:
         for element in final_list:
             cursor.execute("""INSERT INTO facilities (text)
                                VALUES (%s);""",element)
             connection.commit()

