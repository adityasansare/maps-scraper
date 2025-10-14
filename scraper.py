import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def run_scraper(query):
    results = []
    if not query:
        return results

    # Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        search_url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}/"
        driver.get(search_url)
        time.sleep(5)

        # Scroll results to load more
        for _ in range(15):
            driver.execute_script("document.querySelector('div[role=\"feed\"]').scrollBy(0, 1000);")
            time.sleep(random.uniform(1, 2))

        listings = driver.find_elements(By.CSS_SELECTOR, "a[href*='/maps/place/']")

        for i, listing in enumerate(listings, start=1):
            try:
                name = listing.get_attribute("aria-label")
                url = listing.get_attribute("href")

                if not name or not url:
                    continue

                # Open each listing in a new tab
                driver.execute_script("window.open(arguments[0]);", url)
                driver.switch_to.window(driver.window_handles[1])
                time.sleep(random.uniform(3, 5))

                try:
                    category = driver.find_element(By.CSS_SELECTOR, "button[jsaction*='pane.rating.category']").text
                except:
                    category = None
                try:
                    address = driver.find_element(By.CSS_SELECTOR, "button[data-item-id*='address']").text
                except:
                    address = None
                try:
                    phone = driver.find_element(By.CSS_SELECTOR, "button[data-item-id*='phone']").text
                except:
                    phone = None
                try:
                    website = driver.find_element(By.CSS_SELECTOR, "a[data-item-id*='authority']").get_attribute("href")
                except:
                    website = None

                results.append({
                    "query": query,
                    "name": name,
                    "category": category,
                    "address": address,
                    "phone": phone,
                    "website": website,
                    "listing_url": url,
                })

                driver.close()
                driver.switch_to.window(driver.window_handles[0])

            except Exception as e:
                print(f"❌ Error on listing {i}: {e}")
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                continue

    finally:
        driver.quit()

    return results
