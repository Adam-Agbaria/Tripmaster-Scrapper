from flask import Flask, request, jsonify
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import re
import time
import random
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def create_search_url(trip_type, departure_date, return_date, origin, destination, adults, children):
    base_url = "https://booking.kayak.com/flights"
    route = f"{origin}-{destination}"
    departure_date_formatted = datetime.datetime.strptime(departure_date, "%d/%m/%Y").strftime("%Y-%m-%d")
    return_date_formatted = datetime.datetime.strptime(return_date, "%d/%m/%Y").strftime("%Y-%m-%d") if return_date else None
    adults_param = f"{adults}adults"
    children_param = f"children-{'-'.join(['11'] * int(children))}" if int(children) > 0 else ""
    dates = f"{departure_date_formatted}/{return_date_formatted}" if trip_type.lower() != "one way" else f"{departure_date_formatted}"
    # Construct the URL
    url = f"{base_url}/{route}/{dates}/{adults_param}"
    if children_param:
        url += f"/{children_param}"
    url += "?sort=bestflight_a"
    return url

def scrape_flight_data(url):
    options = Options()
    options.headless = True
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"user-agent={'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}")
    options.add_argument("--disable-gpu")
    options.add_argument("--log-level=3")

    driver = webdriver.Chrome(options=options)
    logging.debug(f"Accessing URL: {url}")
    driver.get(url)

    # Wait for the page to load
    time.sleep(random.uniform(5, 10))

    # Scroll down to load more content if needed
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(5, 10))
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    results = []

    flights = driver.find_elements(By.CLASS_NAME, "resultInner")
    logging.debug(f"Number of flights found: {len(flights)}")
    for flight in flights:
        try:
            booking_link = flight.find_element(By.CLASS_NAME, "booking-link")
            aria_label = booking_link.get_attribute('aria-label')
            logging.debug(f"Aria Label: {aria_label}")

            price_match = re.search(r"[\$\€\₪]\d{1,3}(,\d{3})*", aria_label)
            price = price_match.group(0) if price_match else "N/A"
            logging.debug(f"Price: {price}")

            airline_match = re.search(r"for (.*?) flight", aria_label)
            airline = airline_match.group(1) if airline_match else "N/A"
            logging.debug(f"Airline: {airline}")

            if airline.startswith("all passengers., for "):
                airline = airline.replace("all passengers., for ", "").strip()

            link = booking_link.get_attribute('href')
            logging.debug(f"Booking Link: {link}")

            legs = flight.find_elements(By.CLASS_NAME, "flight")
            if len(legs) >= 2:
                outbound_leg = legs[0]
                return_leg = legs[1]

                outbound_depart_time_element = outbound_leg.find_element(By.CLASS_NAME, "depart-time")
                outbound_depart_time = outbound_depart_time_element.text.strip() if outbound_depart_time_element else "N/A"
                outbound_depart_meridiem_element = outbound_leg.find_element(By.CLASS_NAME, "time-meridiem")
                outbound_depart_meridiem = outbound_depart_meridiem_element.text.strip() if outbound_depart_meridiem_element else "N/A"
                logging.debug(f"Outbound Departure Time: {outbound_depart_time} {outbound_depart_meridiem}")

                outbound_arrival_time_element = outbound_leg.find_element(By.CLASS_NAME, "arrival-time")
                outbound_arrival_time = outbound_arrival_time_element.text.strip() if outbound_arrival_time_element else "N/A"
                outbound_arrival_meridiem_element = outbound_leg.find_element(By.CLASS_NAME, "time-meridiem")
                outbound_arrival_meridiem = outbound_arrival_meridiem_element.text.strip() if outbound_arrival_meridiem_element else "N/A"
                logging.debug(f"Outbound Arrival Time: {outbound_arrival_time} {outbound_arrival_meridiem}")

                return_depart_time_element = return_leg.find_element(By.CLASS_NAME, "depart-time")
                return_depart_time = return_depart_time_element.text.strip() if return_depart_time_element else "N/A"
                return_depart_meridiem_element = return_leg.find_element(By.CLASS_NAME, "time-meridiem")
                return_depart_meridiem = return_depart_meridiem_element.text.strip() if return_depart_meridiem_element else "N/A"
                logging.debug(f"Return Departure Time: {return_depart_time} {return_depart_meridiem}")

                return_arrival_time_element = return_leg.find_element(By.CLASS_NAME, "arrival-time")
                return_arrival_time = return_arrival_time_element.text.strip() if return_arrival_time_element else "N/A"
                return_arrival_meridiem_element = return_leg.find_element(By.CLASS_NAME, "time-meridiem")
                return_arrival_meridiem = return_arrival_meridiem_element.text.strip() if return_arrival_meridiem_element else "N/A"
                logging.debug(f"Return Arrival Time: {return_arrival_time} {return_arrival_meridiem}")

                if all(x != "N/A" for x in [airline, price, outbound_depart_time, outbound_arrival_time, return_depart_time, return_arrival_time]):
                    results.append({
                        'airline': airline,
                        'price': price,
                        'outboundDeparture': f"{outbound_depart_time} {outbound_depart_meridiem}",
                        'outboundArrival': f"{outbound_arrival_time} {outbound_arrival_meridiem}",
                        'returnDeparture': f"{return_depart_time} {return_depart_meridiem}",
                        'returnArrival': f"{return_arrival_time} {return_arrival_meridiem}",
                        'link': link
                    })
        except Exception as e:
            logging.error(f"Error while processing flight: {e}")
            continue

    driver.quit()
    logging.debug(f"Results: {results}")
    return results



@app.route('/scrape', methods=['GET'])
def search_flights():
    trip_type = request.args.get('tripType')
    departure_date = request.args.get('departureDate')
    return_date = request.args.get('returnDate')
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    adults = request.args.get('adults')
    children = request.args.get('children')

    url = create_search_url(trip_type, departure_date, return_date, origin, destination, adults, children)
    logging.debug(f"Search URL: {url}")
    results = scrape_flight_data(url)
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8085)

