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

    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")

    # Adjust these selectors if the HTML structure differs, but often it's consistent
    headLines = soup.find_all("li", attrs={"class": "contentlist_article__TSSz5"})

    details = []
    for headline in headLines:
        title_tag = headline.find("a", attrs={"class": "contentlist_title__GRPR1"})
        if title_tag:
            title = title_tag.get_text(strip=True)
            link = title_tag.get("href", "")
            full_link = link if link.startswith("http") else f"https://www.cbc.ca{link}"

            author, pub_date, summary = scrape_article_details(full_link, headers)
            details.append({
                "TITLE": title,
                "LINK": full_link,
                "AUTHOR": author,
                "PUBLISHED_DATE": pub_date,
                "SUMMARY": summary
            })
            print(f"{title} — {full_link} — {author} — {pub_date}")

    return details


def scrape_article_details(article_url, headers):
    page = requests.get(article_url, headers=headers, timeout=10)
    soup = BeautifulSoup(page.text, "html.parser")

    # Try multiple methods to locate author
    author_tag = soup.find("a", class_="byline_authorLink__ML5rs")
    if not author_tag:
        author_tag = soup.find("meta", attrs={"name": "author"})

    author = (author_tag.get_text(strip=True) if author_tag and hasattr(author_tag, "get_text")
              else (author_tag.get("content", "").strip() if author_tag else "N/A"))

    # Published date
    date_tag = soup.find("meta", attrs={"property": "article:published_time"})
    pub_date = date_tag.get("content", "") if date_tag else "N/A"

    # Summary or description
    desc_tag = soup.find("meta", attrs={"name": "description"})
    summary = desc_tag.get("content", "").strip() if desc_tag else "N/A"

    return author, pub_date, summary


def save_json(data, path="details_latest.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_csv(data, path="details_latest.csv"):
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["TITLE", "LINK", "AUTHOR", "PUBLISHED_DATE", "SUMMARY"])
        writer.writeheader()
        writer.writerows(data)


if __name__ == "__main__":
    url = "https://www.cbc.ca/lite/news?sort=latest"
    scraped_data = scrape_site(url)
    save_json(scraped_data, path="details_latest.json")
    save_csv(scraped_data, path="details_latest.csv")
