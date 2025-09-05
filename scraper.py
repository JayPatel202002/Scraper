from bs4 import BeautifulSoup
import requests
import csv
import json

def scrape_site(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/115.0 Safari/537.36"
    }

    page_to_scrap = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(page_to_scrap.text, "html.parser")

    headLines = soup.findAll("li", attrs={"class": "contentlist_article__TSSz5"})

    details = []
    for headline in headLines:
        title_tag = headline.find("a", attrs={"class": "contentlist_title__GRPR1"})
        if title_tag:
            title = title_tag.text.strip()
            link = title_tag.get("href", "")
            full_link = link if link.startswith("http") else "https://www.cbc.ca" + link

            # fetch article page to get author
            author = scrape_author(full_link, headers)

            details.append({"TITLE": title, "LINK": full_link, "AUTHOR": author})
            print(title, "-", full_link, "-", author)

    return details


def scrape_author(article_url, headers):
    """Fetch the author name from the article page"""
    page = requests.get(article_url, headers=headers, timeout=10)
    soup = BeautifulSoup(page.text, "html.parser")

    author_tag = soup.find("span", attrs={"class": "byline__name"})
    if author_tag:
        return author_tag.text.strip()
    return "N/A"


def save_json(data, path="details.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_csv(data, path="details.csv"):
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["TITLE", "LINK", "AUTHOR"])
        writer.writeheader()
        writer.writerows(data)


scrape = scrape_site("https://www.cbc.ca/lite/news?sort=editors-picks")
save_json(scrape)
save_csv(scrape)
