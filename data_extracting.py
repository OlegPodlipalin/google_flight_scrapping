import scrapping

# source to be imported
source = 'https://www.google.com/travel/flights?q=' \
             'Flights%20to%20PAR%20from%20TLV%20on%202022-12-20%20through%202022-12-30%20one-way&curr=EUR'
soup = scrapping.scrape_data(source)
