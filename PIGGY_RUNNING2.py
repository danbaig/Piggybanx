from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import time
import re
from fill_FormsPiggy import fill_form

def check_website_status1(url):
    """
    Check if the website redirects to another URL indicating it is closed.
    """
    response = requests.get(url, allow_redirects=True)
    print(response.url)
    if response.url != url:
        return "Closed"
    return "Open"

def extract_unique_links_from_html(url):
    """
    Extract unique product links from the provided URL's HTML content.
    """
    links = set()
    # Fetch the HTML content from the URL
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    # Find all divs with class "card__content"
    card_content_divs = soup.find_all('div', class_='card__content')
    for div in card_content_divs:
        # Find all h3 tags with class "card__heading" within each div
        h3_tags = div.find_all('h3', class_='card__heading')
        for h3 in h3_tags:
            a_tag = h3.find('a', href=True)
            if a_tag:
                links.add(a_tag['href'])  # Add the link to the set
    return list(links)

def main():
    url = "https://piggybanxinc.com/"
    url1="https://piggybanxinc.com/collections/all"

    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ensure GUI is off
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Path to your ChromeDriver
    webdriver_service = Service()  # Update this path

    # Create a new instance of the Chrome driver
    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
    print(url[:-1])
    try:
        while True:
            status = check_website_status1(url)
            if status == 'Open':
                links = extract_unique_links_from_html(url1)
                for link in links:
                    # Open the URL
                    driver.get(url[:-1] + link)
                    try:
                        # Find the "Add to Cart" button using a regular expression
                        buttons = driver.find_elements(By.CSS_SELECTOR, 'button[id^="ProductSubmitButton-template--"]')
                        add_to_cart_button = None
                        for button in buttons:
                            if re.match(r'ProductSubmitButton-template--\d+__main', button.get_attribute('id')):
                                add_to_cart_button = button
                                break
                        # Attempt to click the "Add to Cart" button
                        if add_to_cart_button and not add_to_cart_button.get_attribute('disabled'):
                            add_to_cart_button.click()
                            driver.save_screenshot('cart.png')
                            print(f"Added product to cart: {link}")
                            checkout_button = WebDriverWait(driver, 10).until(
                                   EC.element_to_be_clickable((By.CLASS_NAME, 'cart__ctas'))
                             )
                            checkout_button.click()
                            # Allow some time for the action to complete (you can adjust this if needed)
                            WebDriverWait(driver, 10).until(
                               EC.url_contains('checkout')
                            )
                            fill_form(driver=driver)
                            # Save the checkout HTML again after navigating to checkout page
                            with open('checkout.html', 'w', encoding='utf-8') as f:
                                f.write(driver.page_source)
                            driver.save_screenshot('checkout.png')
                            print(f"Checked out product: {link}")

                            
                        else:
                            print(f"Product is sold out: {link}")
                    except Exception as e:
                        print(f"Error occurred while trying to add product to cart: {link}. Error: {e}")

            print(f"The website is {status}.")
              
    finally:
        driver.quit()

if __name__ == "__main__":
    main()