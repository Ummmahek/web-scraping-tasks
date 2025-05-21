import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

CHROME_DRIVER_PATH = r"C:\chromedriver-win64\chromedriver-win64\chromedriver.exe"
BASE_URL = "https://schaechter.asmblog.org/schaechter/talmudic_questions/page/{}"

def setup_browser():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def page_has_cloudflare_challenge(driver):
    # Try detecting typical Cloudflare challenge forms or texts
    try:
        # Classic challenge form
        if driver.find_element(By.CSS_SELECTOR, 'div#challenge-form'):
            return True
    except NoSuchElementException:
        pass
    try:
        # Newer Cloudflare "Checking your browser" or title
        page_source = driver.page_source.lower()
        if "checking your browser" in page_source:
            return True
    except Exception:
        pass
    try:
        if "attention required! | cloudflare" in driver.title.lower():
            return True
    except Exception:
        pass
    return False

def wait_for_captcha_solve(driver):
    print("[!] Cloudflare challenge detected. Please solve the CAPTCHA in the browser window now...")
    while page_has_cloudflare_challenge(driver):
        print("Waiting for CAPTCHA to be solved...")
        time.sleep(5)
    print("[+] CAPTCHA solved, continuing scraping.")

def extract_posts(driver):
    posts_data = []
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.entry"))
        )
        entries = driver.find_elements(By.CSS_SELECTOR, "div.entry")
        for entry in entries:
            try:
                title_elem = entry.find_element(By.CSS_SELECTOR, "h3.entry-header a")
                content_elem = entry.find_element(By.CSS_SELECTOR, "div.entry-body")
                title = title_elem.text.strip()
                content = content_elem.text.strip()
                if "Talmudic Question" in title:
                    posts_data.append({
                        'title': title,
                        'content': content
                    })
            except NoSuchElementException:
                continue  # Skip if any part is missing
    except TimeoutException:
        print("Timeout waiting for entries to load.")
    except Exception as e:
        print(f"Error extracting posts: {e}")
    return posts_data


def scrape_page(driver, url):
    print(f"Loading {url}")
    driver.get(url)
    
    # Wait for either posts or cloudflare challenge
    time.sleep(2)  # short delay before checks

    # If posts not found, maybe cloudflare challenge is active
    posts = extract_posts(driver)
    if posts:
        return posts
    
    # Check cloudflare challenge presence
    if page_has_cloudflare_challenge(driver):
        wait_for_captcha_solve(driver)
        # Retry extraction after solve
        posts = extract_posts(driver)
        return posts

    # If no posts and no challenge, just return empty list
    return []

def save_posts_to_csv(posts, filename="talmudic_questions.csv"):
    with open(filename, "w", newline='', encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["title", "content"])
        writer.writeheader()
        writer.writerows(posts)
    print(f"[+] Saved {len(posts)} posts to {filename}")

def main():
    driver = setup_browser()
    all_posts = []

    for page_num in range(1, 22):  # adjust page count as needed
        url = BASE_URL.format(page_num)
        posts = scrape_page(driver, url)
        if posts:
            print(f"Found {len(posts)} posts on page {page_num}")
            all_posts.extend(posts)
        else:
            print(f"No posts found on page {page_num}")
        time.sleep(2)  # polite delay between pages

    save_posts_to_csv(all_posts)
    driver.quit()

if __name__ == "__main__":
    main()
