import time
import random
import pandas as pd
import undetected_chromedriver as uc

def run_scraper(query):
    if not query:
        return []

    # Configure Chrome for Render (headless, no GPU, sandbox disabled)
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = uc.Chrome(options=options)

    results = []
    try:
        search_url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}/"
        driver.get(search_url)
        time.sleep(5)

        # Scroll sidebar to load listings
        for _ in range(10):
            driver.execute_script("document.querySelector('div[role=\"feed\"]').scrollBy(0, 1000);")
            time.sleep(random.uniform(1, 2))

        listings = driver.find_elements("css selector", "a[href*='/maps/place/']")

        for i, listing in enumerate(listings[:50], start=1):  # limit to 50 to avoid timeout
            try:
                name = listing.get_attribute("aria-label")
                url = listing.get_attribute("href")
                if not name or not url:
                    continue

                driver.execute_script("window.open(arguments[0]);", url)
                driver.switch_to.window(driver.window_handles[1])
                time.sleep(random.uniform(3, 5))

                try:
                    category = driver.find_element("css selector", "button[jsaction*='pane.rating.category']").text
                except:
                    category = None
                try:
                    address = driver.find_element("css selector", "button[data-item-id*='address']").text
                except:
                    address = None
                try:
                    phone = driver.find_element("css selector", "button[data-item-id*='phone']").text
                except:
                    phone = None
                try:
                    website = driver.find_element("css selector", "a[data-item-id*='authority']").get_attribute("href")
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
