import pymysql.cursors


def create_db():
    """Creates DB if it doesn't exist yet"""
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='rootroot',
                                 cursorclass=pymysql.cursors.DictCursor)
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(f"""CREATE DATABASE if not exists Google_flight""")
            try:
                cursor.execute(f"""CREATE DATABASE Google_flight""")
            except:  # TODO - specific exception to be raised
                print('DB already exists')
                pass
        connection.commit()


def create_db_tables():
    """Create Tables in DB and Insert values into table facilities"""
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='rootroot',
                                 database='Google_flight',
                                 cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()
    print('hiiii')
    exit()

    try:
        cursor.execute("""CREATE TABLE flights (
                          id_flight INT PRIMARY KEY AUTO_INCREMENT,
                          trip_id INT,
                          country_code INT,
                          departure_time DATETIME,
                          departure_airport_id INT,
                          arrival_time DATETIME,
                          arrival_airport_id INT,
                          flight_duration DATETIME,
                          co2_emission INT,
                          flight_order_in_trip INT,
                          FOREIGN KEY (trip_id) REFERENCES trips(id_trips))
                          FOREIGN KEY (departure_airport_id) REFERENCES airports(id_airport))
                          FOREIGN KEY (arrival_airport_id) REFERENCES airports(id_airport)) """)

        cursor.execute("""CREATE TABLE facilities (
                          id_facilities INT PRIMARY KEY AUTO_INCREMENT,
                          text VARCHAR(50))""")

        cursor.execute("""CREATE TABLE flight_facilities (
                          flight_id INT,
                          facility_id INT,
                          FOREIGN KEY (flight_id) REFERENCES flights(id_flight),
                          FOREIGN KEY (facility_id) REFERENCES facilities(id_facilities))""")

        cursor.execute("""CREATE TABLE trips (
                          id_trips INT PRIMARY KEY AUTO_INCREMENT,
                          unique_id VARCHAR(50),
                          date_of_scrape DATE,
                          price INT)""")

        cursor.execute("""CREATE TABLE airports (
                          id_airport INT PRIMARY KEY AUTO_INCREMENT,
                          abbreviation VARCHAR(50),
                          name VARCHAR(50),
                          city VARCHAR(50),
                          FOREIGN KEY (id_search) REFERENCES search_params(id_search))""")
        connection.commit()

    except:  # TODO - specific exception to be raised
        pass


if __name__ == '__main__':
    create_db()
    create_db_tables()
