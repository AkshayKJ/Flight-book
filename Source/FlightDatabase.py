"""
This is a script that allows the user to collect flight information of one way trip.
This takes advantage of Google Flights and scrapes all the required information from it.
A list of Airports along with theie IATA codes are extracted from https://airports-list.com/
"""


import sqlite3
import requests

from bs4 import BeautifulSoup
import time
from dateutil.parser import parse

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

headers = {
    'User-Agent':
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}


def clean(s):
    """
    Method to remove Titles from given string based on requirement.
    :param s: Input string
    :return s: Modified string
    """
    return s[s.index(':') + 2:-4]


def rabsolute(s):
    """
    Method to concatenate string parts of a HTML tag
    :param s: HTML Tags
    :return k: String
    """
    k = ""
    for x in s:
        k += x.string
    return k


def findname(code):
    """
    Method to find name of the city. Some cities were missing from the website database.
    :param code:  IATA code
    :return city: Name of the city
    """
    url = r'https://airports-list.com/airport/' + code
    source_code = requests.get(url, headers=headers, verify=True).text
    soup = BeautifulSoup(source_code, 'html.parser')
    details = soup.find('div', {'class': 'view-content'})
    city = clean(str(details.find('div', {'class': 'views-field views-field-field-gorod-eng'}).find('p')))
    return city


def make_IATA_database():
    """
    Method to create the database of all available IATA coded airports. This method is to be called only once
    and the database created will act as a base database to search destinations.
    :return None:
    """
    database = sqlite3.connect('Flights')
    db = database.cursor()
    query = "CREATE TABLE IF NOT EXISTS IATA(CODE VARCHAR(3) PRIMARY KEY, CITY VARCHAR UNIQUE, NAME VARCHAR,COUNTRY VARCHAR)"
    db.execute(query)

    alpha = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    for x in alpha:
        url = r'http://www.nationsonline.org/oneworld/IATA_Codes/IATA_Code_{}.htm'.format(x)
        source_code = requests.get(url, headers=headers, verify=True).text
        soup = BeautifulSoup(source_code, 'html.parser')
        for code in soup.findAll('tr'):
            c = 0
            t = tuple()
            for info in code.findAll('td', {'class': 'border1'}):
                if info.string == None and c == 0:
                    break
                elif info.string == None and c == 1:
                    try:
                        t += (rabsolute(info.findAll('a')),)
                    except TypeError or AttributeError:
                        t += (findname(t[0]),)

                else:
                    t += (info.string,)
                c += 1
            if len(t) == 4 and len(t[0]) == 3:
                # print(t)
                db.execute("INSERT OR REPLACE INTO IATA VALUES(?,?,?,?)", t)
    database.commit()
    database.close()


# make_IATA_database()


def get_segment_data(segment):
    """
    This method extracts the reqired data from the HTML tag of google flights website.
    Information like Departure time, Airport name, Arrival time, Airline code, Flight number etc.
    The nomenclature is easy enough to understand.
    :param segment: '.gws-flights-results__leg' object from BeautifulSoup
    :return data: Dictionary containing data
    """
    data = {}
    departure_data = list(
        segment.find(
            class_='gws-flights-results__leg-departure').stripped_strings)
    data['dep_time'] = departure_data[0]
    data['dep_airport_long'] = departure_data[1]
    data['dep_airport_code'] = departure_data[2]

    arrival_data = list(
        segment.find(
            class_='gws-flights-results__leg-arrival').stripped_strings)
    if len(arrival_data) == 3:
        data['arr_time'] = arrival_data[0]
        data['arr_airport_long'] = arrival_data[1]
        data['arr_airport_code'] = arrival_data[2]
    else:
        data['arr_time'] = arrival_data[0]
        data['arr_airport_long'] = arrival_data[2]
        data['arr_airport_code'] = arrival_data[3]

    flight_data = list(
        segment.find(
            class_='gws-flights-results__leg-flight').stripped_strings)
    data['airline'] = flight_data[0]
    data['seat_class'] = flight_data[1]
    data['airplane'] = flight_data[2]
    data['airline_code'] = flight_data[3]
    try:
        data['flight_number'] = flight_data[4] + flight_data[5]
    except IndexError:
        data['flight_number'] = flight_data[3] + flight_data[4]

    return data


def scrape(url):
    """
    Driver for scraping. Contains code to save the collected information into the database. Contains the main crawler.
    Using Selenium and BeautifulSoup4 to collect data from website and parsing. Using the web driver PhantomJS.
    :param url: URL for scraping
    :return:
    """
    # ['flight_date', 'full_duration', 'segments', 'stops', 'flight_number', 'arr_airport_long', 'arr_airport_code',
    # 'dep_time', 'airplane', 'arr_time', 'airline_code', 'dep_airport_code', 'dep_airport_long',
    # 'airline', 'seat_class']
    database = sqlite3.connect('Flights')
    db = database.cursor()
    query = "CREATE TABLE IF NOT EXISTS FLIGHTS(FLIGHT_NUMBER VARCHAR PRIMARY KEY,FLIGHT_DATE DATE,DURATION FLOAT," \
            " STOPS INTEGER, DEPT_AIRPORT_NAME VARCHAR, DEPT_AIRPORT_CODE VARCHAR, DEPART_TIME VARCHAR ,AIRLINE VARCHAR," \
            "AIRPLANE VARCHAR,ARR_TIME VARCHAR, ARR_AIRPORT_CODE VARCHAR, ARR_ARIPORT_NAME VARCHAR," \
            " SEAT VARCHAR,PRICE INTEGER )"
    db.execute(query)

    # driver = webdriver.PhantomJS('phantomjs.exe')
    options=webdriver.ChromeOptions()
    options.add_argument('headless');
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url)
    timeout = 10
    try:
        element_present = EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, '.gws-flights-results__unpriced-airlines'),
            'Prices are not available for: Southwest. Flights with unavailable prices are at the end of the list.'
        )
        WebDriverWait(driver, timeout).until(element_present)
        time.sleep(1)
    except TimeoutException:
        print("Timed out waiting for page to load")

    soup = BeautifulSoup(driver.page_source, 'lxml')
    flights = []
    all_results = soup.find_all(
        class_='gws-flights-widgets-expandablecard__body')
    for n in range(len(all_results)):
        dict = {}
        stops = list(
            driver.find_elements_by_css_selector(
                '.gws-flights-results__stops'))[n].text.strip()
        try:
            n_stops = int(stops[0])
        except ValueError:
            n_stops = 0
        dict['stops'] = n_stops

        collapsed_itinerary = list(
            soup.find_all(
                class_='gws-flights-results__collapsed-itinerary'))[n]
        full_duration = collapsed_itinerary.find(
            class_='gws-flights-results__duration').get_text()
        full_duration = str(full_duration).split(" ")
        hours = int(full_duration[0][:-1])
        try:
            minutes = int(full_duration[1][:-1])
        except IndexError:
            minutes = 0
            hours = hours/60
        dict['full_duration'] = round(hours + (minutes / 60), 2)

        flight_date = list(
            list(
                soup.find_all(
                    class_=
                    'gws-flights-results__itinerary-details-heading-text'))[
                n].stripped_strings)[1]
        dict['flight_date'] = parse(flight_date).date()

        price = list(
            collapsed_itinerary.find(
                class_='gws-flights-results__itinerary-price')
                .stripped_strings)[0][1:]
        price = str(price).replace(',', '')

        dict['price'] = int(price[1:])

        dict['segments'] = []
        segments = list(all_results)[n].find_all(
            class_='gws-flights-results__leg')
        for segment in segments:
            dict['segments'] = get_segment_data(segment)

        flights.append(dict)
        database_tuple = (dict['segments']['flight_number'], dict['flight_date'], dict['full_duration'],
                          dict['stops'], dict['segments']['dep_airport_long'],
                          dict['segments']['dep_airport_code'], dict['segments']['dep_time'],
                          dict['segments']['airline'],
                          dict['segments']['airplane'], dict['segments']['arr_time'],
                          dict['segments']['arr_airport_code'],
                          dict['segments']['arr_airport_long'], dict['segments']['seat_class'], dict['price'])
        # Inserting into database
        db.execute("INSERT OR REPLACE INTO FLIGHTS VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", database_tuple)
    database.commit()
    database.close()
    return


def makeurl(origin, destination, dep_date, passengers):
    """
    Converts source, destination, date and passengers into valid flights.google URL
    :param origin: Source passenger
    :param destination: Destination of passenger
    :param dep_date: Departure Date
    :param passengers: Number of passengers 0<p<10
    :return None:
    """
    url = \
        'https://www.google.com/flights#' \
        + 'flt=' \
        + origin \
        + '.' \
        + destination \
        + '.' \
        + dep_date \
        + ';c:INR' \
        + ';e:1;sd:1;t:f;tt:o'

    if passengers != 1:
        url = url + ';px:' + str(passengers)
    scrape(url)
    return
make_IATA_database()