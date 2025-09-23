from bs4 import BeautifulSoup
import requests
import csv
import json
import re


def scrape_site(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/115.0 Safari/537.36"
    }

    page = requests.get(url, headers=headers, timeout=10)
    page.raise_for_status()
    soup = BeautifulSoup(page.text, "html.parser")

    items = soup.findAll("li", attrs={"class": "contentlist_article__TSSz5"})           

    details = []
    for item in items:
        a = item.find("a", attrs={"class": "contentlist_title__GRPR1"})
        if not a:
            continue
        title = a.get_text(strip=True)
        href = a.get("href", "")
        full_link = href if href.startswith("http") else "https://www.cbc.ca" + href
        print(title, "-", full_link)

        # Fetch the article page and print the article's own title and first paragraph
        article_title = "N/A"
        first_paragraph = "N/A"
        try:
            article_page = requests.get(full_link, headers=headers, timeout=10)
            article_page.raise_for_status()
            article_soup = BeautifulSoup(article_page.text, "html.parser")
            h1 = article_soup.find("h2", attrs={"class": "article_title__djYX0"})
            article_title = h1.get_text(strip=True) if h1 else "N/A"

            # Extract byline (author | outlet | posted | updated)
            byline = "N/A"
            try:
                author_anchor = article_soup.select_one('a[class*="byline_authorLink"]')
                if author_anchor:
                    p = author_anchor.find_parent('p')
                    if p:
                        for svg in p.find_all('svg'):
                            svg.decompose()
                        byline_text = p.get_text(" ", strip=True)
                        if byline_text:
                            byline = byline_text
                if byline == "N/A":
                    # Fallback: search for a <p> containing both "CBC News" and "Posted:"
                    for p in article_soup.find_all('p'):
                        txt = p.get_text(" ", strip=True)
                        if "CBC News" in txt and "Posted:" in txt:
                            byline = txt
                            break
            except Exception:
                pass

            # First paragraph: prefer first element with class article_segment__aglub (div or p)
            segment_el = article_soup.select_one(
                "article .article_segment__aglub, main .article_segment__aglub, .article_segment__aglub"
            )
            if segment_el:
                seg_text = segment_el.get_text(strip=True)
                if seg_text:
                    first_paragraph = seg_text
            # Fallback to paragraphs inside <article> or <main>
            if first_paragraph == "N/A":
                container = article_soup.find("div") #or article_soup.find("main") or article_soup
                if container:
                    for cand in container.find_all("div"):
                        text = cand.get_text(strip=True)
                        if len(text.split()) > 4:
                            first_paragraph = text
                            break

            print("Article page title:", article_title)
            print("Byline:", byline)
            print("First paragraph:", first_paragraph)
        except Exception as e:
            print("Article fetch failed ->", e)

        details.append({"TITLE": article_title or title, "LINK": full_link, "BYLINE": byline, "FIRST_PARAGRAPH": first_paragraph})

    return details


def save_json(data, path="details.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_csv(data, path="details.csv"):
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["TITLE", "LINK", "BYLINE", "FIRST_PARAGRAPH"])
        writer.writeheader()
        writer.writerows(data)


if __name__ == "__main__":
    scrape = scrape_site("https://www.cbc.ca/lite/news?sort=editors-picks")
    save_json(scrape)
    save_csv(scrape)
