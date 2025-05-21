import requests
from bs4 import BeautifulSoup
import csv
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "https://pubmed.ncbi.nlm.nih.gov"
SEARCH_TERM = "myxobacteria genome"
RESULTS_PER_PAGE = 100
MAX_PAGES = 5
MAX_WORKERS = 5  # Controls concurrency (safe level)
OUTPUT_FILE = "pubmed_results.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def build_search_url(page):
    return f"{BASE_URL}/?term={SEARCH_TERM.replace(' ', '+')}&sort=date&size={RESULTS_PER_PAGE}&page={page}"

def get_article_links(soup):
    links = soup.select("a.docsum-title")
    return [BASE_URL + link["href"] for link in links]

def get_article_data(article_url):
    try:
        # Add random delay to avoid overloading server
        time.sleep(random.uniform(0.5, 1.2))

        response = requests.get(article_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")

        title_tag = soup.find("h1", class_="heading-title")
        title = title_tag.get_text(strip=True) if title_tag else "N/A"

        authors_tag = soup.find("div", class_="authors-list")
        authors = authors_tag.get_text(separator=", ", strip=True) if authors_tag else "N/A"

        details_tag = soup.find("div", class_="cit")
        details = details_tag.get_text(strip=True) if details_tag else "N/A"

        abstract_tag = soup.find("div", class_="abstract-content")
        abstract = abstract_tag.get_text(separator=" ", strip=True) if abstract_tag else "N/A"

        return {
            "Title": title,
            "Authors": authors,
            "Details": details,
            "Abstract": abstract,
            "URL": article_url
        }

    except Exception as e:
        print(f"Error fetching {article_url}: {e}")
        return None

def scrape_pubmed():
    all_results = []

    for page in range(1, MAX_PAGES + 1):
        print(f"\n[INFO] Processing page {page}...")
        search_url = build_search_url(page)

        try:
            response = requests.get(search_url, headers=HEADERS)
            soup = BeautifulSoup(response.content, "html.parser")
        except Exception as e:
            print(f"[ERROR] Failed to fetch search results page {page}: {e}")
            continue

        article_links = get_article_links(soup)
        print(f"[INFO] Found {len(article_links)} articles on page {page}")

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(get_article_data, url): url for url in article_links}

            for future in as_completed(futures):
                result = future.result()
                if result:
                    all_results.append(result)

        # Respectful delay between result pages
        time.sleep(2)

    return all_results

def save_to_csv(data, filename):
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Title", "Authors", "Details", "Abstract", "URL"])
        writer.writeheader()
        writer.writerows(data)

def main():
    print("[START] Beginning PubMed scrape...")
    results = scrape_pubmed()
    save_to_csv(results, OUTPUT_FILE)
    print(f"\n[DONE] Saved {len(results)} articles to '{OUTPUT_FILE}'.")

if __name__ == "__main__":
    main()
