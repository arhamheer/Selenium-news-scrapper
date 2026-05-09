from flask import Flask, request, Response
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import json
from urllib.parse import quote_plus

app = Flask(__name__)

REGISTRATION = "FA23-BAI-027"
NEWS_SOURCE = "ProPakistani"
NEWS_BASE = "https://propakistani.pk"


def get_chrome_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(30)
    return driver


def summarize_text(text, max_sentences=4):
    text = re.sub(r'\s+', ' ', text).strip()
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 40]
    summary = ' '.join(sentences[:max_sentences])
    if len(summary) > 1200:
        summary = summary[:1200].rsplit(' ', 1)[0] + '...'
    return summary if summary else text[:500]


def scrape_propakistani(keyword):
    driver = get_chrome_driver()
    article_url = ""
    summary = ""

    try:
        # ProPakistani uses Google Custom Search - correct URL format
        search_url = f"https://propakistani.pk/search/?q={quote_plus(keyword)}#gsc.tab=0&gsc.q={quote_plus(keyword)}&gsc.page=1"
        driver.get(search_url)

        # Wait for Google Custom Search results to load (JS rendered)
        wait = WebDriverWait(driver, 15)
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.gsc-result")))
        except Exception:
            time.sleep(6)  # fallback wait

        time.sleep(3)  # extra wait for all results to render

        article_link = None

        # Google Custom Search result links are inside .gsc-result .gs-title a
        gsc_selectors = [
            "//div[contains(@class,'gsc-result')]//a[contains(@class,'gs-title')]",
            "//div[contains(@class,'gsc-result')]//a[@class='gs-title']",
            "//div[contains(@class,'gs-result')]//a",
            "//a[contains(@class,'gs-title')]",
        ]

        all_links = []
        for sel in gsc_selectors:
            try:
                els = driver.find_elements(By.XPATH, sel)
                for el in els:
                    href = el.get_attribute("href") or ""
                    # GSC links are sometimes wrapped - get data-ctorig for real URL
                    real = el.get_attribute("data-ctorig") or href
                    if "propakistani.pk" in real and re.search(r'/20\d\d/', real):
                        all_links.append(real)
            except Exception:
                continue

        if all_links:
            article_link = all_links[0]
        else:
            # Fallback: try all <a> tags on page for propakistani article links
            all_a = driver.find_elements(By.TAG_NAME, "a")
            for a in all_a:
                href = a.get_attribute("href") or ""
                real = a.get_attribute("data-ctorig") or href
                if "propakistani.pk" in real and re.search(r'/20\d\d/', real):
                    all_links.append(real)
                    break
            if all_links:
                article_link = all_links[0]

        article_url = article_link if article_link else search_url

        # Fetch the article page
        driver.get(article_url)
        time.sleep(3)

        content_selectors = [
            "//div[contains(@class,'entry-content')]//p",
            "//div[contains(@class,'post-content')]//p",
            "//div[contains(@class,'article-content')]//p",
            "//article//p",
            "//main//p",
        ]

        paragraphs = []
        for sel in content_selectors:
            try:
                els = driver.find_elements(By.XPATH, sel)
                if els:
                    paragraphs = [e.text.strip() for e in els if len(e.text.strip()) > 40]
                    if paragraphs:
                        break
            except Exception:
                continue

        if paragraphs:
            summary = summarize_text(' '.join(paragraphs))
        else:
            body_text = driver.find_element(By.TAG_NAME, "body").text
            summary = summarize_text(body_text)

    except Exception as e:
        summary = f"Error during scraping: {str(e)}"
        if not article_url:
            article_url = NEWS_BASE
    finally:
        driver.quit()

    return article_url, summary


@app.route("/get", methods=["GET"])
def get_news():
    keyword = request.args.get("keyword", "").strip()
    if not keyword:
        return Response(
            json.dumps({"error": "Missing 'keyword' query parameter"}),
            status=400,
            mimetype="application/json"
        )
    try:
        url, summary = scrape_propakistani(keyword)
        result = {
            "registration": REGISTRATION,
            "newssource": NEWS_SOURCE,
            "keyword": keyword,
            "url": url,
            "summary": summary
        }
        return Response(
            json.dumps(result, indent=2),
            status=200,
            mimetype="application/json"
        )
    except Exception as e:
        result = {
            "registration": REGISTRATION,
            "newssource": NEWS_SOURCE,
            "keyword": keyword,
            "url": NEWS_BASE,
            "summary": f"Scraping failed: {str(e)}"
        }
        return Response(
            json.dumps(result, indent=2),
            status=500,
            mimetype="application/json"
        )


@app.route("/", methods=["GET"])
def index():
    return f"""
    <html><body style='font-family:sans-serif;padding:40px;max-width:600px'>
      <h1>DevOps Quiz 3 - Selenium News Scraper</h1>
      <p><b>Registration:</b> {REGISTRATION}</p>
      <p><b>News Source:</b> {NEWS_SOURCE}</p>
      <p><b>Try it:</b> <a href='/get?keyword=pakistan'>/get?keyword=pakistan</a></p>
    </body></html>
    """


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7000, debug=False)