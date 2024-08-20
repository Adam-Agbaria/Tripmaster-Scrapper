# Scraper Server

This project is a web scraping service designed to fetch flight and hotel data from popular booking websites like Kayak and Booking.com. Built using Flask, it provides a RESTful API interface that allows users to search for flights and hotels by providing the necessary parameters such as city, check-in dates, flight routes, and more.

## Key Features

### Flight Scraper (Kayak)

- **Selenium Automation**: The flight scraper leverages Selenium to automate browser interactions, enabling the scraping of dynamic web content from Kayak's flight booking pages.
- **Headless Browsing**: The scraper operates in headless mode, minimizing the overhead of rendering a full browser window.
- **Flexible Search Parameters**: Users can search for flights based on trip type (one-way or round-trip), origin, destination, number of passengers, and travel dates.
- **Data Extraction**: Extracts crucial details such as airline, price, departure, and arrival times from the search results.

### Hotel Scraper (Booking.com)

- **BeautifulSoup Parsing**: The hotel scraper uses BeautifulSoup to parse HTML content and extract hotel names, booking links, and prices from Booking.com.
- **Currency Conversion**: Hotel prices in local currency (ILS) are automatically converted to USD using a predefined exchange rate.
- **Customizable Search**: Users can search for hotels based on city, check-in/check-out dates, number of adults, children, and rooms.

## Technologies Used

- **Flask**: Lightweight Python web framework used to build RESTful APIs.
- **Selenium**: Web automation tool used to scrape dynamic content from booking websites.
- **BeautifulSoup**: HTML parsing library for scraping and extracting data from static web pages.
- **Requests**: Simple HTTP library used to fetch HTML content from booking sites.
- **Logging**: Comprehensive logging to monitor scraping operations and provide debug information.

## API Endpoints

### Flight Scraper Endpoint

- **GET `/scrape`**: Scrapes flight information from Kayak based on the provided search parameters.

#### Parameters:
- `tripType`: One-way or round-trip.
- `departureDate`: Date of departure in `dd/mm/yyyy` format.
- `returnDate`: Date of return in `dd/mm/yyyy` format (optional for one-way trips).
- `origin`: IATA code of the origin airport.
- `destination`: IATA code of the destination airport.
- `adults`: Number of adult passengers.
- `children`: Number of child passengers.

### Hotel Scraper Endpoint

- **GET `/scrape`**: Scrapes hotel information from Booking.com based on the provided search parameters.

#### Parameters:
- `city`: Name of the city where you want to search for hotels.
- `checkInDate`: Check-in date in `dd/mm/yyyy` format.
- `checkOutDate`: Check-out date in `dd/mm/yyyy` format.
- `adults`: Number of adults staying in the hotel.
- `children`: Number of children staying in the hotel.
- `rooms`: Number of rooms required.