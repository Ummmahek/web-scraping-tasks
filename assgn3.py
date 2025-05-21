import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# URL to scrape
url = "https://www.imdb.com/chart/top/"  # Example website

# Headers to bypass some website restrictions
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Make a request to the webpage
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

# Extract the script tag containing JSON data
script_tag = soup.find('script', type="application/ld+json")
if script_tag:
    json_data = json.loads(script_tag.string)
else:
    print("No JSON data found.")
    exit()

# Prepare data for the DataFrame
titles = [item.get('item', {}).get('name', 'No Title') for item in json_data.get('itemListElement', [])]
ratings = [item.get('item', {}).get('aggregateRating', {}).get('ratingValue', 'No Rating') for item in json_data.get('itemListElement', [])]
genres = [item.get('item', {}).get('genre', 'No Genre') for item in json_data.get('itemListElement', [])]
links = [item.get('item', {}).get('url', 'No URL') for item in json_data.get('itemListElement', [])]

# Function to scrape year and director from an IMDb movie page
def scrape_movie_details(movie_url):
    # Set up Selenium WebDriver (headless mode)
    chrome_options = Options()
    chrome_options.headless = True  # Run Chrome in headless mode (no GUI)
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    # Specify path to the ChromeDriver
    driver_service = Service(r"C:\chromedriver-win64\chromedriver-win64\chromedriver.exe")  # Update path to your chromedriver
    driver = webdriver.Chrome(service=driver_service, options=chrome_options)
    
    # Open the movie page
    driver.get(movie_url)
    time.sleep(5)  # Allow time for the page to load

    # Scrape the year and director
    try:
        # Year of release
        year = driver.find_element(By.XPATH, "//a[contains(@href, 'releaseinfo') and contains(@class, 'ipc-link')]").text
        
        # Director
        director = driver.find_element(By.XPATH, "//a[@class='ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link']").text
    except Exception as e:
        print(f"Error extracting details from {movie_url}: {e}")
        year = 'N/A'
        director = 'N/A'

    # Quit the driver after scraping
    driver.quit()

    return year, director

# List to store the year and director information
years = []
directors = []

# Loop through the movie links and scrape year and director
for link in links:
    full_url = link  # Construct the full movie URL
    print(f"Scraping {full_url}...")  # Print current URL being scraped
    year, director = scrape_movie_details(full_url)
    years.append(year)
    directors.append(director)

# Create a DataFrame with all the data
df = pd.DataFrame({
    'Title': titles,
    'Rating': ratings,
    'Genres': genres,
    'Link': links,
    'Year': years,
    'Director': directors
})

# Specify the folder path where you want to save the Excel file
output_path = r"C:\Users\Mahek\Desktop\python_vs\imdb_top_250.csv"

# Save the DataFrame to an Excel file in the specified folder
df.to_excel(output_path, index=False)

print(f"Data saved to {output_path}")