# google_flight_scrapping
### data mining project for ITC
<p align="center">
<img src="img/ITC_logo.png" width=150></p>


**********MILESTONE 1********** 


This program parses the [Google Flights](https://www.google.com/travel/flights/), a research engine for finding and booking flights. 
<br>The program opens a page according to the specific users request, parses informagion about avaliable flight options and stores it in database. 
Program made by Oleg Podlipalin and Ruben Adhoute during ITC October 2022 Data Science cohort.

### How to run it
- Download __*.zip__ archive
- Unzip it at any suitable folder
- Install required libraries and packages according to __requirements.txt__
- Run __main.py__ script from command line with your request options (use _main.py -h_ option to see help information about all options)
- The program allows to scrape multiple destinations/date of a trip
  
The scraping process is time consuming so make shure you have a cup of coffee :).  
For your conviniance there are status bars with information about scraping process for all chromedriver instances.  
Simultaneously can be run up to four chromedriver instances. If your request include more than four specific trips to be scraped they will be processed in these four inctances in turn.

```

```

### Run options
The program allows following options:  
-h, --help - help information about running the script.  
-d, --dest - destination parameter (required). Takes in a list of desirable destinations by their number separated by space from list of possible destinations: [ 1:Paris, 2:Berlin, 3:Amsterdam, 4:Rome, 5:Madrid ]   
-t, --term - date of trip parameter (required). Takes in a list of all the desirable dates of flight in <DD-MM-YYYY> format separated by space  
-f, --flight_class - flight class option patameter (optional). Allows to user choose flight class. Choices: [ business, economy ], default: [ economy ]  
-w, --wait - optional parameter thet allows to user change the maximum delay time for webpage to be loaded in seconds. Default: [ 5 ]  
-s, --silent - optional parameter that allows to user to run the script without opening a browser window.


### Program structure

| *File*             | *Purpose*                             | *Description*                                                                        |
|--------------------|---------------------------------------|--------------------------------------------------------------------------------------|
| __main.py__ | the main script  | Runs and maintains the entire process of scraping. Calls different classes and functions to generate chromedriver instanse, scrape [Google Flights](https://www.google.com/travel/flights/) search result for provided data. Contains two functions: __create_urls__ to build urls in accordance with user's input, and __scrape__ to run and maintaine the scraping process for several destinations simultaneously using __multiprocessing__ library. Creates up to four threads with unique chromedriver instance in them that can be reused for different url requests scraping (if provided more than four requests in total). |
|
| __cli.py__ | the command line interface script | Contains __GetInput__ class. This class provides to user options to specify his request by providing required information and chosing optional settings. Parses input from command line using __argparse__ library. |
|
|  __driver.py__ | the script to create __chromedriver__ instance  | Contains __Driver__ class. When it is called it creates an independent instance of chromedriver (does not depend on url to scrape). Takes in parameters to set options for driver: run silently, set time delay to _waiter_ instance. |
|
| __scraper.py__   | the script to scrape [Google Flights](https://www.google.com/travel/flights/) search results | Contains __GoogleFlightsScraper__ class. This class takes in a Driver class instance and url to be scrapped as input parameters. This script uses private methods to open and extend all the flights options for particular request. As a result of its work creates a BeautifulSoup object in its __.soup__ proterty. |
|
|  __parser.py__   | the script to extract data from [Google Flights](https://www.google.com/travel/flights/) HTML code (BeautifulSoup object) | Contains __GoogleFlightsParser__ class. This class takes in a BeautifulSoup object as an input parameter. This script extracts data about every possible flight option and collects it in json-like structure in its __.flights__ property. |
|
| __get_from_library.py__ | the auxiliary script to extract information from libraries | Contains __get_data__ function. This function opens __.json__ file, reads it and returns received content as a result of its execution |
|