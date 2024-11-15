from bs4 import BeautifulSoup
import requests
import csv


walmart_prefix = "https://www.walmart.com"


def get_soup(url, headers):
    """Get the BeautifulSoup object for a given URL."""
    page = requests.get(url, headers=headers)
    return BeautifulSoup(page.content, "html.parser")


def extract_product_title(product):
    """Extract the title of the product."""
    title_tag = product.find("span", {"data-automation-id": "product-title"})
    return title_tag.text if title_tag else "No title available"


def extract_product_link(product):
    """Extract the product link."""
    link_element = product.find(
        "a", class_="w-100 h-100 z-1 hide-sibling-opacity absolute"
    )
    href_value = (
        link_element["href"] if link_element and link_element.get("href") else ""
    )

    return (
        href_value
        if href_value.startswith(walmart_prefix)
        else f"{walmart_prefix}{href_value}"
    )


def extract_product_price(product):
    """Extract the product price."""
    price_container = product.find("div", {"data-automation-id": "product-price"})

    if price_container:
        price_whole = (
            price_container.find("span", class_="f2").text
            if price_container.find("span", class_="f2")
            else "0"
        )
        price_fraction_tag = price_container.find("span", style="vertical-align:0.75ex")
        price_fraction = price_fraction_tag.text if price_fraction_tag else "00"
        return f"${price_whole}.{price_fraction}"
    return "Price not found"


def extract_product_rating(product):
    """Extract the product rating."""
    rating_tag = product.find("span", {"data-testid": "product-ratings"})
    return (
        rating_tag["data-value"]
        if rating_tag and rating_tag.get("data-value")
        else "No rating"
    )


def extract_reviewer_count(product):
    """Extract the number of reviewers."""
    reviewer_count_tag = product.find("span", {"data-testid": "product-reviews"})
    return (
        reviewer_count_tag["data-value"]
        if reviewer_count_tag and reviewer_count_tag.get("data-value")
        else "No reviews"
    )


def extract_product_data(product):
    """Extract all relevant product data."""
    title = extract_product_title(product)
    link = extract_product_link(product)
    price = extract_product_price(product)
    rating = extract_product_rating(product)
    reviewer_count = extract_reviewer_count(product)

    return [title, link, price, rating, reviewer_count]


def scrape_page_products(page_number, headers):
    """Scrape products from a specific page."""
    url = f"https://www.walmart.com/search?q=groceries&page={page_number}&affinityOverride=store_led"
    soup = get_soup(url, headers)
    product_result_div = soup.find("div", {"data-testid": "item-stack"})

    if product_result_div:
        products = product_result_div.find_all("div", {"role": "group"})
        return [extract_product_data(product) for product in products]
    return []


def write_products_to_csv(filename, pages, headers):
    """Scrape products from multiple pages and write to a CSV file."""
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Title", "Link", "Price", "Product Rating", "Reviewer Count"])

        for page_number in range(1, pages + 1):
            print(f"Scraping page {page_number}...\n")
            products_data = scrape_page_products(page_number, headers)

            for product_data in products_data:
                writer.writerow(product_data)
                print(product_data)


# User-agent headers
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
}

# Scrape 10 pages of Walmart products and write to CSV
write_products_to_csv("walmart.csv", pages=10, headers=headers)

print("Data has been successfully written to walmart.csv.")