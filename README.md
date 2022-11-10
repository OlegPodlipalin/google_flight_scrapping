# google_flight_scrapping
### data mining project for ITC
<p align="center">
<img src="img/ITC_logo.png" width=150></p>


**********MILESTONE 1********** 


This program parses oogleflight, a research engine for booking flight. 
<br>Parsing page, getting important information about flighs according to a specific research. 
Program made by Oleg Podlipalin and Ruben Adhoute during ITC October 2022 Data Science cohort.

### How to run it
- Download __*.zip__ file
- Unzip it at any suitable folder
- Install all libs from __requirements.txt__
- Fill in the _CHOOSE_YOUR_OPTION_ parametr (destination)
- Run __data_extracting.py__
- Have a cup of cofee
- That's all
```

```


### Functionality of functions
Functions are broken down to files. Each file combines logically connected functionality.

| *File*             | *Function*               | *What do and return*                                                                                       |
|--------------------|--------------------------|------------------------------------------------------------------------------------------------------------|
| data_extracting.py | main                     | Acts as an orchestrator to program functions. Calls different functions to generate driver and scrap data. |
| scrapping.py       | scrape_data              | Activate driver and running it on the web page                                                             |
| driver_action.py   | click_object_class_name  | tell driver to execute the following - click on class object                                               |
| driver_action.py   | click_object_xpath       | tell driver to execute the following - click on xpath object                                               |
| driver_action.py   | extend_all               | tell driver to execute the following - extend object                                                       |
| driver_action.py   | xpath_build              | tell driver to execute the following - build xpath from object                                             |
| driver_start.py    | start_driver             | initialize the driver given a specific URL                                                                 |