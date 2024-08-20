from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define the exchange rate (hardcoded for this example)
EXCHANGE_RATE = 3.75

# Function to create a search query URL for Booking.com based on user input
def create_booking_url(city, check_in_date, check_out_date, adults, children, rooms):
    # Convert dates from dd/mm/yyyy to yyyy-mm-dd format
    checkin_day, checkin_month, checkin_year = check_in_date.split('/')
    checkout_day, checkout_month, checkout_year = check_out_date.split('/')

    # Construct the URL for the search query
    url = (f"https://www.booking.com/searchresults.html?ss={city.replace(' ', '+')}"
           f"&checkin_year={checkin_year}&checkin_month={checkin_month}&checkin_monthday={checkin_day}"
           f"&checkout_year={checkout_year}&checkout_month={checkout_month}&checkout_monthday={checkout_day}"
           f"&group_adults={adults}&group_children={children}&no_rooms={rooms}")
    return url

# Function to extract hotel names, links, and prices from the BeautifulSoup object
def extract_hotel_names_links_prices(soup):
    hotels = []
    # Find hotel names, links, and prices based on the provided HTML structure
    results = soup.find_all('div', {'data-testid': 'property-card'})
    for result in results:
        name_tag = result.find('a', {'data-testid': 'title-link'})
        price_tag = result.find('span', {'data-testid': 'price-and-discounted-price'})
        if name_tag and price_tag:
            name = name_tag.get_text(strip=True).replace('Opens in new window', '').strip()
            link = name_tag['href']
            price_text = price_tag.get_text(strip=True).replace('\xa0', ' ')
            
            # Extract the numeric part of the price
            price_ils = float(price_text.replace('₪', '').replace(',', '').strip())
            
            # Convert the price to USD
            price_usd = round(price_ils / EXCHANGE_RATE)
            
            # Format the price in USD
            price_usd_formatted = f"{price_usd}$"
            
            if name and link and price_usd_formatted:
                hotels.append({
                    'hotel_name': name,
                    'url': link,
                    'price': price_usd_formatted
                })
    return hotels

@app.route('/scrape', methods=['GET'])
def search_hotels():
    city = request.args.get('city')
    check_in_date = request.args.get('checkInDate')
    check_out_date = request.args.get('checkOutDate')
    adults = request.args.get('adults')
    children = request.args.get('children')
    rooms = request.args.get('rooms')

    logger.debug(f"Received parameters: city={city}, check_in_date={check_in_date}, check_out_date={check_out_date}, adults={adults}, children={children}, rooms={rooms}")

    # Generate the search URL
    search_url = create_booking_url(city, check_in_date, check_out_date, adults, children, rooms)
    
    # Log the search URL
    logger.debug(f"Search URL: {search_url}")

    # Set up the headers to mimic a browser visit
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    # Fetch the content from the URL
    response = requests.get(search_url, headers=headers)
    logger.debug(f"HTTP response status: {response.status_code}")

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract hotel names, links, and prices
    hotels = extract_hotel_names_links_prices(soup)

    # Log the extracted hotel details
    logger.debug(f"Extracted hotels: {hotels}")

    # Return the list of hotels as JSON
    return jsonify(hotels)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8086)
