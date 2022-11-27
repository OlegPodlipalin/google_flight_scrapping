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
            except:
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

    try:
        cursor.execute("""CREATE TABLE if not exists trips(
                          id INT PRIMARY KEY AUTO_INCREMENT,
                          unique_id VARCHAR(50),
                          date_of_scrape DATETIME,
                          price INT)""")

        cursor.execute("""CREATE TABLE if not exists airports (
                          id VARCHAR(50) PRIMARY KEY,
                          abbreviation VARCHAR(50),
                          name VARCHAR(50),
                          city VARCHAR(50))""")

        cursor.execute("""CREATE TABLE if not exists facilities(
                          id INT PRIMARY KEY AUTO_INCREMENT,
                          text VARCHAR(50))""")


        cursor.execute("""CREATE TABLE if not exists flights(
                          id INT PRIMARY KEY AUTO_INCREMENT,
                          trip_id INT,
                          departure_time TIME,
                          departure_airport_id VARCHAR(50),
                          arrival_time TIME,
                          arrival_airport_id VARCHAR(50),
                          flight_duration TIME,
                          co2_emission VARCHAR(50),
                          flight_order_in_trip INT,
                          FOREIGN KEY (trip_id) REFERENCES trips(id))""")
        # FOREIGN
        # KEY(departure_airport_id)
        # REFERENCES
        # airports(id),
        # FOREIGN
        # KEY(arrival_airport_id)
        # REFERENCES
        # airports(id))

        cursor.execute("""CREATE TABLE if not exists flight_facilities (
                          flight_id INT,
                          facility_id INT)""")
        # FOREIGN
        # KEY(flight_id)
        # REFERENCES
        # flights(id),
        # FOREIGN
        # KEY(facility_id)
        # REFERENCES
        # facilities(id))

        connection.commit()
    except:
        print('Issue with table creation')
        pass


if __name__ == '__main__':
    create_db()
    create_db_tables()
