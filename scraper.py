import requests
from bs4 import BeautifulSoup
import time

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# ─────────────────────────────────────
# 1. KOMPAS  →  https://www.kompas.com/global
# ─────────────────────────────────────
def scrape_kompas(limit=5):
    url = "https://www.kompas.com/global"
    articles = []
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        for item in soup.select(".hlItem"):
            link_tag = item.select_one("a.hlItem-link")
            img_tag  = item.select_one(".hlImg img")
            title_tag= item.select_one(".hlTitle")

            if not (link_tag and img_tag and title_tag):
                continue

            articles.append({
                "source": "Kompas",
                "title" : title_tag.get_text(strip=True),
                "link"  : link_tag["href"],
                "image" : img_tag.get("src", "")
            })

            if len(articles) >= limit:
                break

    except Exception as e:
        print(f"[Kompas] Error: {e}")

    return articles


# ─────────────────────────────────────
# 2. TRIBUN  →  https://m.tribunnews.com/internasional
# ─────────────────────────────────────
def scrape_tribun(limit=5):
    url = "https://m.tribunnews.com/internasional"
    articles = []
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        # Semua article ada di #latestul > div.pa15.bdr
        container = soup.select_one("#latestul")
        if not container:
            return articles

        for item in container.select("div.pa15.bdr"):
            # Filter: hanya item yang punya kategori "Internasional"
            cat_tag = item.select_one("h4 a.fbo2.tsa-2")
            if not cat_tag or "internasional" not in cat_tag.get_text(strip=True).lower():
                continue

            img_tag   = item.select_one(".btsquare img")
            title_tag = item.select_one("h3 a.fbo2.f16")

            if not (img_tag and title_tag):
                continue

            articles.append({
                "source": "Tribun",
                "title" : title_tag.get_text(strip=True),
                "link"  : title_tag["href"],
                "image" : img_tag.get("src", "")
            })

            if len(articles) >= limit:
                break

    except Exception as e:
        print(f"[Tribun] Error: {e}")

    return articles


# ─────────────────────────────────────
# 3. VIVA  →  https://www.viva.co.id/berita/dunia
# ─────────────────────────────────────
def scrape_viva(limit=5):
    url = "https://www.viva.co.id/berita/dunia"
    articles = []
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        for item in soup.select(".article-list-row"):
            img_tag   = item.select_one(".article-list-thumb img")
            title_tag = item.select_one("a.article-list-title")

            if not (img_tag and title_tag):
                continue

            # Viva pakai data-original untuk URL gambar asli; fallback ke src
            image_url = img_tag.get("data-original") or img_tag.get("src", "")

            articles.append({
                "source": "Viva",
                "title" : title_tag.select_one("h2").get_text(strip=True) if title_tag.select_one("h2") else title_tag.get_text(strip=True),
                "link"  : title_tag["href"],
                "image" : image_url
            })

            if len(articles) >= limit:
                break

    except Exception as e:
        print(f"[Viva] Error: {e}")

    return articles


# ─────────────────────────────────────
# Gabungan: ambil dari 3 sumber
# ─────────────────────────────────────
def get_all_news(limit_per_source=5):
    kompas = scrape_kompas(limit_per_source)
    time.sleep(1)          # jeda sopan ke server
    tribun = scrape_tribun(limit_per_source)
    time.sleep(1)
    viva   = scrape_viva(limit_per_source)

    # Gabung & campur urutan: Kompas[0], Tribun[0], Viva[0], Kompas[1], ...
    combined = []
    max_len  = max(len(kompas), len(tribun), len(viva))
    for i in range(max_len):
        if i < len(kompas):  combined.append(kompas[i])
        if i < len(tribun):  combined.append(tribun[i])
        if i < len(viva):    combined.append(viva[i])

    return combined


# ─────────────────────────────────────
# Test langsung (jalankan: python scraper.py)
# ─────────────────────────────────────
if __name__ == "__main__":
    news = get_all_news(limit_per_source=3)
    for i, item in enumerate(news, 1):
        print(f"\n[{i}] ({item['source']})")
        print(f"    Judul : {item['title']}")
        print(f"    Link  : {item['link']}")
        print(f"    Gambar: {item['image']}")
