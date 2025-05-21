import requests
from bs4 import BeautifulSoup
import time
import random
import csv

# Custom headers to mimic a real browser
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
}

# Retry logic for fetching article page
def fetch_article_page(url, retries=3):
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return BeautifulSoup(response.content, "html.parser")
        except Exception as e:
            print(f"Retry {attempt + 1} for {url} failed: {e}")
            time.sleep(random.uniform(3, 6))
    print(f"Failed to retrieve {url} after {retries} attempts.")
    return None

# Base search URL and parameters
base_url = "https://www.ncbi.nlm.nih.gov/pmc/"
search_url = f"{base_url}?term=(myxobacteria)+AND+genome"

# Output CSV file
output_file = "pmc_mxyobacteria_genome_articles.csv"

# Open CSV for writing
with open(output_file, mode="w", newline="", encoding="utf-8") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["Title", "Authors", "Journal", "Date", "PMCID", "Abstract"])

    page = 1
    while True:
        print(f"Scraping page {page}...")
        page_url = f"{search_url}&page={page}"
        res = requests.get(page_url, headers=headers)

        if res.status_code != 200:
            print(f"Failed to retrieve page {page}. Status code: {res.status_code}")
            break

        soup = BeautifulSoup(res.content, "html.parser")
        articles = soup.select("div.rprt")

        if not articles:
            print("No more articles found.")
            break

        for article in articles:
            try:
                title_tag = article.find("a")
                title = title_tag.get_text(strip=True) if title_tag else "N/A"
                href = title_tag["href"] if title_tag else None
                article_url = href if href.startswith("http") else "https://www.ncbi.nlm.nih.gov" + href if href else None

                authors_tag = article.find("div", class_="desc")
                authors = authors_tag.get_text(strip=True) if authors_tag else "N/A"

                details_tag = article.find("div", class_="details")
                journal_info = details_tag.get_text(strip=True) if details_tag else "N/A"

                pmcid_tag = article.find("dl", class_="rprtid")
                pmcid = pmcid_tag.get_text(strip=True).split(":")[-1] if pmcid_tag else "N/A"

                abstract = "N/A"
                if article_url:
                    art_soup = fetch_article_page(article_url)
                    if art_soup:
                        abs_div = art_soup.find("div", class_="abstr")
                        if abs_div:
                            abstract = abs_div.get_text(separator=" ", strip=True)

                writer.writerow([title, authors, journal_info, "", pmcid, abstract])
                time.sleep(random.uniform(3, 6))  # polite delay

            except Exception as e:
                print(f"Error parsing article: {e}")
                continue

        page += 1
        if page > 5:  # limit to 5 pages for safety; remove or increase as needed
            break

print(f"\nScraping complete. Results saved to '{output_file}'.")
