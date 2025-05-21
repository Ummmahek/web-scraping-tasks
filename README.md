# 🕸️ Web Scraping Projects

This repository contains a series of web scraping scripts implemented using Python. The projects demonstrate scraping data from various real-world websites using libraries like `BeautifulSoup`, `Selenium`, and concurrency tools like `ThreadPoolExecutor`. Each script focuses on a specific use case — from e-commerce data extraction to academic article mining.

---

## 📁 Contents

### 1. `assgn1.py` - Amazon Product Scraper
Scrapes product information such as **title**, **price**, **rating**, **reviews**, and **availability** for Lenovo i5 laptops from Amazon.

- **Tools Used**: `requests`, `BeautifulSoup`, `pandas`
- **Output**: `lenovo_laptops.csv`
- **Note**: Includes polite delays and user-agent headers to avoid being blocked.

---

### 2. `assgn2.py` - Talmudic Questions Blog Scraper
Scrapes **titles** and **contents** of blog posts from the *"Talmudic Questions"* section of the ASM Microbiology blog.

- **Tools Used**: `Selenium`, `BeautifulSoup`
- **Features**: Handles Cloudflare CAPTCHA manually.
- **Output**: `talmudic_questions.csv`

---

### 3. `assgn3.py` - IMDb Top 250 Movies Scraper
Scrapes data for the **Top 250 IMDb movies**, including **title**, **rating**, **genre**, **year**, and **director**.

- **Tools Used**: `requests`, `BeautifulSoup`, `Selenium`, `json`, `pandas`
- **Output**: `imdb_top_250.csv`
- **Note**: Uses Selenium to fetch additional metadata per movie (director/year).

---

### 4. `assgn4.py` - PMC Myxobacteria Genome Article Scraper
Scrapes metadata and abstracts of articles related to **"myxobacteria genome"** from **PubMed Central (PMC)**.

- **Tools Used**: `requests`, `BeautifulSoup`, `csv`
- **Features**: Resilient request handling with retries and polite delays.
- **Output**: `pmc_mxyobacteria_genome_articles.csv`

---

### 5. `assgn5.py` - PubMed Myxobacteria Genome Scraper with Concurrency
Efficiently scrapes article data (title, authors, abstract, etc.) related to **"myxobacteria genome"** from **PubMed**, using multithreading.

- **Tools Used**: `requests`, `BeautifulSoup`, `concurrent.futures`, `csv`
- **Features**: Concurrent scraping with polite randomized delays and error handling.
- **Output**: `pubmed_results.csv`

---


