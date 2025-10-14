# backend/scraper.py
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, random

def scrape_google_maps(query, max_results=5):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Firefox(options=options)
    wait = WebDriverWait(driver, 15)

    def get_text_safe(by, selector):
        try:
            el = wait.until(EC.presence_of_element_located((by, selector)))
            return el.text.strip()
        except:
            return None

    def extract_coordinates(url):
        try:
            parts = url.split("!3d")[1].split("!4d")
            lat = parts[0]
            lng = parts[1].split("!")[0]
            return lat, lng
        except:
            return None, None

    data = []
    search_url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}/"
    driver.get(search_url)
    time.sleep(6)

    try:
        wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@aria-label, 'Results for')]")))
    except:
        driver.quit()
        raise Exception("Results container not found")

    scroll_box = driver.find_element(By.XPATH, "//div[contains(@aria-label, 'Results for')]")
    for _ in range(10):
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_box)
        time.sleep(2)

    listings = driver.find_elements(By.XPATH, "//a[contains(@href, '/maps/place/')]")

    links = []
    for l in listings:
        href = l.get_attribute("href")
        name = l.get_attribute("aria-label")
        if href and href not in links and name:
            links.append(href)

    for i, link in enumerate(links[:max_results], start=1):
        try:
            driver.get(link)
            time.sleep(random.uniform(4, 6))

            name = get_text_safe(By.XPATH, "//h1[contains(@class, 'DUwDvf fontHeadlineLarge')]")
            if not name:
                name = get_text_safe(By.CSS_SELECTOR, "h1")

            category = get_text_safe(By.XPATH, "//button[contains(@aria-label, 'category')]/div/div[2]")
            rating = get_text_safe(By.XPATH, "//span[contains(@aria-label, 'stars')]")
            reviews = get_text_safe(By.XPATH, "//span[contains(text(),'reviews') or contains(text(),'Ratings')]")
            address = get_text_safe(By.XPATH, "//button[contains(@data-item-id, 'address')]/div/div[2]")
            phone = get_text_safe(By.XPATH, "//button[contains(@data-item-id, 'phone:tel')]/div/div[2]")
            website = get_text_safe(By.XPATH, "//a[contains(@data-item-id, 'authority')]/div/div[2]")
            lat, lng = extract_coordinates(driver.current_url)

            data.append({
                "query": query,
                "name": name,
                "category": category,
                "rating": rating,
                "reviews": reviews,
                "address": address,
                "phone": phone,
                "website": website,
                "latitude": lat,
                "longitude": lng,
                "listing_url": link
            })

        except Exception as e:
            print(f"Error scraping listing {i}: {e}")
            continue

    driver.quit()
    return data
