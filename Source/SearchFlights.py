
def get_segment_data(segment):
    """
    Input: a '.gws-flights-results__leg' object from BeautifulSoup
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
    data['arr_time'] = arrival_data[0]
    data['arr_airport_long'] = arrival_data[1]
    data['arr_airport_code'] = arrival_data[2]

    flight_data = list(
        segment.find(
            class_='gws-flights-results__leg-flight').stripped_strings)
    data['airline'] = flight_data[0]
    data['seat_class'] = flight_data[1]
    data['airplane'] = flight_data[2]
    data['airline_code'] = flight_data[3]
    data['flight_number'] = flight_data[4] + flight_data[5]

    return data


def scrape(url):
    driver = webdriver.Chrome('chromedriver.exe')
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
        minutes = int(full_duration[1][:-1])
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
                .stripped_strings)[0]
        try:
            dict['price'] = int(price[1:])
        except:
            pass

        dict['segments'] = []
        segments = list(all_results)[n].find_all(
            class_='gws-flights-results__leg')
        for segment in segments:
            dict['segments'] = get_segment_data(segment)

        # amenities = list(driver.find_elements_by_css_selector('.gws-flights-results__amenities'))[n].text.split('\n')
        flights.append(dict)
        # print(dict.keys(), dict['segments'])

    return flights


def makeurl(origin, destination, dep_date, passengers):
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
    return url


print(scrape(makeurl('BOM', 'DEL', '2018-11-11', 11)))
