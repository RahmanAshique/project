import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
from requests.exceptions import ConnectionError


def retry_connection(url, retries=3, wait_time=5):
    """Retry making a request in case of DNS resolution failures."""
    for attempt in range(retries):
        try:
            response = requests.get(url)
            print(f"Connection successful on attempt {attempt + 1}")
            return True
        except ConnectionError as e:
            print(f"Connection failed (Attempt {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print("Max retries reached. Exiting.")
                return False


def initialize_driver(url, retries=3, wait_time=5):
    """Initialize the Selenium WebDriver with retry logic for DNS issues."""
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    
    # Retry DNS resolution before using Selenium WebDriver
    if retry_connection(url, retries, wait_time):
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        driver.set_window_size(1200, 900)
        print(driver.title)
        return driver
    else:
        print("Failed to initialize driver due to DNS resolution issues.")
        return None


def click_next_page_button(driver):
    """Click the 'Next page' button to load additional products."""
    try:
        # Wait for the next button to be clickable
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.ppn--element.corner[aria-label='Next']"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
        time.sleep(2)  # Allow UI to settle
        driver.execute_script("arguments[0].click();", next_button)
        print('"Next page" button clicked.')
        return True
    except Exception as e:
        print(f"Failed to click the 'Next page' button: {e}")
        return False


def scrape_data(html):
    """Extract product data (title and price) from the HTML content."""
    soup = BeautifulSoup(html, "html.parser")

    # Find the div with class 'products-search--grid searchOnlineResults'
    product_grid = soup.find("div", class_="products-search--grid searchOnlineResults")
    
    if product_grid:
        product_items = product_grid.find_all("div", class_="default-product-tile tile-product item-addToCart")
        products = []
        
        for product in product_items:
            product_info = {
                "Title": extract_product_title(product),
                "Price": extract_product_price(product),
            }
            products.append(product_info)
        
        return products
    else:
        return []


def extract_product_title(product):
    """Extract the product title from the product container."""
    title_tag = product.find("div", class_="head__title")  
    return title_tag.text.strip() if title_tag else "No title available"


def extract_product_price(product):
    """Extract the product price from the product container."""
    price_tag = product.find("span", class_="price-update")  
    return price_tag.text.strip() if price_tag else "Price not available"


def write_csv(dataframe, file_name):
    """Write the DataFrame to a CSV file."""
    dataframe.to_csv(f"{file_name}.csv", index=False)


def main():
    url = "https://www.foodbasics.ca/search?filter=food"
    
    # Initialize the driver with retry logic
    driver = initialize_driver(url)
    
    if driver is None:
        print("Failed to initialize WebDriver. Exiting...")
        return
    
    # Hold all scraped products
    all_products = []
    
    # Click the 'Next page' button up to 10 times, or until it no longer appears
    max_clicks = 100
    for _ in range(max_clicks):
        time.sleep(5)  # Give time for the page to load fully after each click
        
        # Scrape the current page's products
        html = driver.page_source
        products = scrape_data(html)
        all_products.extend(products)  # Append all products from the current page
        print("Products: ", products)
        
        # Try to click the 'Next page' button
        if not click_next_page_button(driver):
            print("No more 'Next page' button found, stopping.")
            break
    
    # Quit the driver after scraping
    driver.quit()
    
    # Create a DataFrame and write to a CSV
    if all_products:
        product_df = pd.DataFrame(all_products)
        write_csv(product_df, "foodbasics_products")
        print("Web Scraping and CSV file writing complete!")
    else:
        print("No products were scraped.")


if __name__ == "__main__":
    main()
