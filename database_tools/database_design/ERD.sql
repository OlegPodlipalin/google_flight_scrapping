CREATE TABLE `flights` (
  `id` int PRIMARY KEY,
  `flight_num` varchar(255),
  `depart_time` datetime,
  `depart_airport_id` int,
  `arr_time` datetime,
  `arr_airport_id` int,
  `flight_duration` time,
  `co2_emission` varchar(255),
  PRIMARY KEY (`id`)
);

CREATE TABLE `airports` (
  `id` int PRIMARY KEY,
  `iata_code` varchar(255),
  `name` varchar(255),
  `city` varchar(255),
  PRIMARY KEY (`id`)
);

CREATE TABLE `trips` (
  `id` int PRIMARY KEY,
  `unique_id` varchar(255),
  `date_of_scrape` date,
  `price` int,
  `destination` varchar(255),
  PRIMARY KEY (`id`)
);

CREATE TABLE `facilities` (
  `id` int PRIMARY KEY,
  `text` varchar(255),
  PRIMARY KEY (`id`)
);

CREATE TABLE `flights_facilities` (
  `flight_id` int,
  `facility_id` int
);

CREATE TABLE `trips_flights` (
  `trip_id` int,
  `flight_id` int,
  `order_in_trip` int
);

ALTER TABLE `trips_flights` ADD FOREIGN KEY (`flight_id`) REFERENCES `flights` (`id`);

ALTER TABLE `trips_flights` ADD FOREIGN KEY (`trip_id`) REFERENCES `trips` (`id`);

ALTER TABLE `flights` ADD FOREIGN KEY (`arr_airport_id`) REFERENCES `airports` (`id`);

ALTER TABLE `flights` ADD FOREIGN KEY (`depart_airport_id`) REFERENCES `airports` (`id`);

ALTER TABLE `flights_facilities` ADD FOREIGN KEY (`flight_id`) REFERENCES `flights` (`id`);

ALTER TABLE `flights_facilities` ADD FOREIGN KEY (`facility_id`) REFERENCES `facilities` (`id`);
