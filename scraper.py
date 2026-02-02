# scraper.py — Direct web-scraping version
# Sumber: CNN Indonesia, Viva, Tribunnews, BBC Indonesia,
#          Kompas, Kumparan, Liputan6, Cakaplah, Detik
import requests
from bs4 import BeautifulSoup
import random
import time
import html as html_mod

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
}

TIMEOUT = 12  # detik

# ─────────────────────────────────────────────────────────
# Placeholder per sumber (fallback kalau tidak ada gambar)
# ─────────────────────────────────────────────────────────
PLACEHOLDERS = {
    "CNN Indonesia":  "https://images.unsplash.com/photo-1588681664899-f142ff2dc9b1?w=400&h=225&fit=crop",
    "Viva":           "https://images.unsplash.com/photo-1611273426858-450d8e3c9fce?w=400&h=225&fit=crop",
    "Tribunnews":     "https://images.unsplash.com/photo-1546410531-bb4caa6b424d?w=400&h=225&fit=crop",
    "BBC Indonesia":  "https://images.unsplash.com/photo-1589652717521-10c0d092dea9?w=400&h=225&fit=crop",
    "Kompas":         "https://images.unsplash.com/photo-1559136555-9303baea8ebd?w=400&h=225&fit=crop",
    "Kumparan":       "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=400&h=225&fit=crop",
    "Liputan6":       "https://images.unsplash.com/photo-1513360371117-8b68a2f6b5a7?w=400&h=225&fit=crop",
    "Cakaplah":       "https://images.unsplash.com/photo-1585386959984-a4155224a1ad?w=400&h=225&fit=crop",
    "Detik":          "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=400&h=225&fit=crop",
}

DEFAULT_PH = "https://images.unsplash.com/photo-1589652717521-10c0d092dea9?w=400&h=225&fit=crop"


def _ph(source):
    return PLACEHOLDERS.get(source, DEFAULT_PH)


def _clean(text: str) -> str:
    """Bersihkan teks dari whitespace berlebih."""
    return " ".join(text.split()).strip()


def _abs_url(base: str, href: str) -> str:
    """Buat URL absolute dari href relatif."""
    if not href:
        return ""
    if href.startswith("http"):
        return href
    if href.startswith("//"):
        return "https:" + href
    if href.startswith("/"):
        return base.rstrip("/") + href
    return base.rstrip("/") + "/" + href


# ═══════════════════════════════════════════════════════════
# SCRAPER PER SUMBER
# ═══════════════════════════════════════════════════════════

def scrape_cnn_indonesia():
    """CNN Indonesia — nasional & internasional"""
    articles = []
    pages = [
        ("https://www.cnnindonesia.com/nasional", "CNN Indonesia", "nasional"),
        ("https://www.cnnindonesia.com/internasional", "CNN Indonesia", "internasional"),
    ]
    for url, source, cat in pages:
        try:
            res = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            soup = BeautifulSoup(res.text, "html.parser")
            # CNN Indonesia menggunakan card dengan class tertentu
            cards = soup.select("div.card-story, div[class*='card'], article")
            for card in cards[:6]:
                a_tag = card.select_one("a[href*='/nasional/'], a[href*='/internasional/'], a[href]")
                title_tag = card.select_one("h2, h3, h4, [class*='title'], [class*='headline']")
                img_tag = card.select_one("img")

                if not a_tag or not title_tag:
                    continue

                title = _clean(title_tag.get_text())
                if len(title) < 10:
                    continue

                link = _abs_url("https://www.cnnindonesia.com", a_tag.get("href", ""))
                image = ""
                if img_tag:
                    image = img_tag.get("src") or img_tag.get("data-src") or img_tag.get("data-lazy-src") or ""
                    image = _abs_url("https://www.cnnindonesia.com", image)

                articles.append({
                    "source": source,
                    "title": title[:150],
                    "link": link,
                    "image": image or _ph(source),
                    "category": cat,
                })
        except Exception as e:
            print(f"  [CNN Indonesia] error ({cat}): {e}")
    return articles


def scrape_viva():
    """Viva.co.id — nasional & internasional"""
    articles = []
    pages = [
        ("https://www.viva.co.id/baru/berita", "Viva", "nasional"),
        ("https://www.viva.co.id/baru/dunia", "Viva", "internasional"),
    ]
    for url, source, cat in pages:
        try:
            res = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            soup = BeautifulSoup(res.text, "html.parser")
            cards = soup.select("div.article-list-item, div[class*='article'], div[class*='news'], article")
            for card in cards[:6]:
                a_tag = card.select_one("a[href]")
                title_tag = card.select_one("h2, h3, h4, [class*='title'], [class*='headline']")
                img_tag = card.select_one("img")

                if not a_tag or not title_tag:
                    continue

                title = _clean(title_tag.get_text())
                if len(title) < 10:
                    continue

                link = _abs_url("https://www.viva.co.id", a_tag.get("href", ""))
                image = ""
                if img_tag:
                    image = img_tag.get("src") or img_tag.get("data-src") or ""
                    image = _abs_url("https://www.viva.co.id", image)

                articles.append({
                    "source": source,
                    "title": title[:150],
                    "link": link,
                    "image": image or _ph(source),
                    "category": cat,
                })
        except Exception as e:
            print(f"  [Viva] error ({cat}): {e}")
    return articles


def scrape_tribunnews():
    """Tribunnews.com — nasional & internasional"""
    articles = []
    pages = [
        ("https://www.tribunnews.com/nasional", "Tribunnews", "nasional"),
        ("https://www.tribunnews.com/dunia", "Tribunnews", "internasional"),
    ]
    for url, source, cat in pages:
        try:
            res = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            soup = BeautifulSoup(res.text, "html.parser")
            cards = soup.select("div.news-list-item, div[class*='news-list'], div[class*='article'], article")
            for card in cards[:6]:
                a_tag = card.select_one("a[href]")
                title_tag = card.select_one("h2, h3, h4, [class*='title'], [class*='headline']")
                img_tag = card.select_one("img")

                if not a_tag or not title_tag:
                    continue

                title = _clean(title_tag.get_text())
                if len(title) < 10:
                    continue

                link = _abs_url("https://www.tribunnews.com", a_tag.get("href", ""))
                image = ""
                if img_tag:
                    image = img_tag.get("src") or img_tag.get("data-src") or ""
                    image = _abs_url("https://www.tribunnews.com", image)

                articles.append({
                    "source": source,
                    "title": title[:150],
                    "link": link,
                    "image": image or _ph(source),
                    "category": cat,
                })
        except Exception as e:
            print(f"  [Tribunnews] error ({cat}): {e}")
    return articles


def scrape_bbc_indonesia():
    """BBC Indonesia — nasional & internasional"""
    articles = []
    pages = [
        ("https://www.bbc.com/indonesia/indonesia", "BBC Indonesia", "nasional"),
        ("https://www.bbc.com/indonesia/dunia", "BBC Indonesia", "internasional"),
    ]
    for url, source, cat in pages:
        try:
            res = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            soup = BeautifulSoup(res.text, "html.parser")
            # BBC sering pakai data-testid atau structure <article>
            cards = soup.select('[data-testid="card"], article[class*="card"], div[class*="card"]')
            if not cards:
                # fallback: cari semua <a> yang mengarah ke artikel
                cards = soup.select("a[href*='/indonesia/']")
            for card in cards[:8]:
                a_tag = card if card.name == "a" else card.select_one("a[href]")
                title_tag = card.select_one("h2, h3, h4, [data-testid*='headline'], [class*='title']")

                if not a_tag:
                    continue

                # Kalau card sendiri adalah <a>, ambil teks langsung
                if not title_tag and card.name == "a":
                    title = _clean(card.get_text())
                else:
                    if not title_tag:
                        continue
                    title = _clean(title_tag.get_text())

                if len(title) < 10 or len(title) > 200:
                    continue

                link = _abs_url("https://www.bbc.com", a_tag.get("href", ""))
                # Pastikan link mengarah ke artikel Indonesia
                if "/indonesia/" not in link:
                    continue

                img_tag = card.select_one("img")
                image = ""
                if img_tag:
                    image = img_tag.get("src") or img_tag.get("data-src") or ""
                    image = _abs_url("https://www.bbc.com", image)

                articles.append({
                    "source": source,
                    "title": title[:150],
                    "link": link,
                    "image": image or _ph(source),
                    "category": cat,
                })
        except Exception as e:
            print(f"  [BBC Indonesia] error ({cat}): {e}")
    return articles


def scrape_kompas():
    """Kompas.com — nasional & internasional"""
    articles = []
    pages = [
        ("https://www.kompas.com/nasional", "Kompas", "nasional"),
        ("https://www.kompas.com/global", "Kompas", "internasional"),
    ]
    for url, source, cat in pages:
        try:
            res = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            soup = BeautifulSoup(res.text, "html.parser")
            cards = soup.select("div.story-card, div[class*='story'], div[class*='article'], article")
            for card in cards[:6]:
                a_tag = card.select_one("a[href]")
                title_tag = card.select_one("h2, h3, h4, [class*='title'], [class*='headline']")
                img_tag = card.select_one("img")

                if not a_tag or not title_tag:
                    continue

                title = _clean(title_tag.get_text())
                if len(title) < 10:
                    continue

                link = _abs_url("https://www.kompas.com", a_tag.get("href", ""))
                image = ""
                if img_tag:
                    image = img_tag.get("src") or img_tag.get("data-src") or ""
                    image = _abs_url("https://www.kompas.com", image)

                articles.append({
                    "source": source,
                    "title": title[:150],
                    "link": link,
                    "image": image or _ph(source),
                    "category": cat,
                })
        except Exception as e:
            print(f"  [Kompas] error ({cat}): {e}")
    return articles


def scrape_kumparan():
    """Kumparan.com — nasional & internasional"""
    articles = []
    pages = [
        ("https://kumparan.com/tag/nasional", "Kumparan", "nasional"),
        ("https://kumparan.com/tag/dunia", "Kumparan", "internasional"),
    ]
    for url, source, cat in pages:
        try:
            res = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            soup = BeautifulSoup(res.text, "html.parser")
            cards = soup.select("div[class*='article'], div[class*='story'], article, div[class*='card']")
            for card in cards[:6]:
                a_tag = card.select_one("a[href]")
                title_tag = card.select_one("h2, h3, h4, [class*='title'], [class*='headline']")
                img_tag = card.select_one("img")

                if not a_tag or not title_tag:
                    continue

                title = _clean(title_tag.get_text())
                if len(title) < 10:
                    continue

                link = _abs_url("https://kumparan.com", a_tag.get("href", ""))
                image = ""
                if img_tag:
                    image = img_tag.get("src") or img_tag.get("data-src") or ""
                    image = _abs_url("https://kumparan.com", image)

                articles.append({
                    "source": source,
                    "title": title[:150],
                    "link": link,
                    "image": image or _ph(source),
                    "category": cat,
                })
        except Exception as e:
            print(f"  [Kumparan] error ({cat}): {e}")
    return articles


def scrape_liputan6():
    """Liputan6.com — nasional & internasional"""
    articles = []
    pages = [
        ("https://www.liputan6.com/nasional", "Liputan6", "nasional"),
        ("https://www.liputan6.com/global", "Liputan6", "internasional"),
    ]
    for url, source, cat in pages:
        try:
            res = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            soup = BeautifulSoup(res.text, "html.parser")
            cards = soup.select("div.news-item, div[class*='article'], div[class*='story'], article")
            for card in cards[:6]:
                a_tag = card.select_one("a[href]")
                title_tag = card.select_one("h2, h3, h4, [class*='title'], [class*='headline']")
                img_tag = card.select_one("img")

                if not a_tag or not title_tag:
                    continue

                title = _clean(title_tag.get_text())
                if len(title) < 10:
                    continue

                link = _abs_url("https://www.liputan6.com", a_tag.get("href", ""))
                image = ""
                if img_tag:
                    image = img_tag.get("src") or img_tag.get("data-src") or ""
                    image = _abs_url("https://www.liputan6.com", image)

                articles.append({
                    "source": source,
                    "title": title[:150],
                    "link": link,
                    "image": image or _ph(source),
                    "category": cat,
                })
        except Exception as e:
            print(f"  [Liputan6] error ({cat}): {e}")
    return articles


def scrape_cakaplah():
    """Cakaplah.com — nasional & internasional"""
    articles = []
    pages = [
        ("https://www.cakaplah.com/berita/nasional", "Cakaplah", "nasional"),
        ("https://www.cakaplah.com/berita/internasional", "Cakaplah", "internasional"),
    ]
    for url, source, cat in pages:
        try:
            res = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            soup = BeautifulSoup(res.text, "html.parser")
            cards = soup.select("div[class*='article'], div[class*='berita'], div[class*='news'], article")
            for card in cards[:6]:
                a_tag = card.select_one("a[href]")
                title_tag = card.select_one("h2, h3, h4, [class*='title'], [class*='headline'], [class*='judul']")
                img_tag = card.select_one("img")

                if not a_tag or not title_tag:
                    continue

                title = _clean(title_tag.get_text())
                if len(title) < 10:
                    continue

                link = _abs_url("https://www.cakaplah.com", a_tag.get("href", ""))
                image = ""
                if img_tag:
                    image = img_tag.get("src") or img_tag.get("data-src") or ""
                    image = _abs_url("https://www.cakaplah.com", image)

                articles.append({
                    "source": source,
                    "title": title[:150],
                    "link": link,
                    "image": image or _ph(source),
                    "category": cat,
                })
        except Exception as e:
            print(f"  [Cakaplah] error ({cat}): {e}")
    return articles


def scrape_detik():
    """Detik.com — nasional & internasional"""
    articles = []
    pages = [
        ("https://news.detik.com/nasional", "Detik", "nasional"),
        ("https://news.detik.com/dunia", "Detik", "internasional"),
    ]
    for url, source, cat in pages:
        try:
            res = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            soup = BeautifulSoup(res.text, "html.parser")
            cards = soup.select("div.news-item, div[class*='news'], div[class*='article'], article")
            for card in cards[:6]:
                a_tag = card.select_one("a[href]")
                title_tag = card.select_one("h2, h3, h4, [class*='title'], [class*='headline']")
                img_tag = card.select_one("img")

                if not a_tag or not title_tag:
                    continue

                title = _clean(title_tag.get_text())
                if len(title) < 10:
                    continue

                link = _abs_url("https://news.detik.com", a_tag.get("href", ""))
                image = ""
                if img_tag:
                    image = img_tag.get("src") or img_tag.get("data-src") or ""
                    image = _abs_url("https://news.detik.com", image)

                articles.append({
                    "source": source,
                    "title": title[:150],
                    "link": link,
                    "image": image or _ph(source),
                    "category": cat,
                })
        except Exception as e:
            print(f"  [Detik] error ({cat}): {e}")
    return articles


# ═══════════════════════════════════════════════════════════
# MASTER SCRAPER
# ═══════════════════════════════════════════════════════════

ALL_SCRAPERS = [
    scrape_cnn_indonesia,
    scrape_viva,
    scrape_tribunnews,
    scrape_bbc_indonesia,
    scrape_kompas,
    scrape_kumparan,
    scrape_liputan6,
    scrape_cakaplah,
    scrape_detik,
]


def get_all_news(limit_per_source=3):
    """
    Jalankan semua scraper, gabungkan, hapus duplikat,
    acak urutan agar setiap refresh menampilkan berita berbeda.
    """
    print("Memulai pengambilan berita dari semua sumber...")
    all_articles = []

    for scraper_fn in ALL_SCRAPERS:
        try:
            print(f"  Jalankan {scraper_fn.__name__}...")
            result = scraper_fn()
            all_articles.extend(result)
            print(f"    → {len(result)} artikel")
        except Exception as e:
            print(f"    ✗ Error: {e}")
        time.sleep(0.5)  # jeda kecil antar sumber

    print(f"\nTotal sebelum dedup: {len(all_articles)}")

    # ── Hapus duplikat berdasarkan judul (case-insensitive, 60 char pertama)
    unique = []
    seen_titles = set()
    seen_links  = set()
    for art in all_articles:
        title_key = art["title"][:60].lower().strip()
        link_key  = art["link"].strip().lower()
        if title_key in seen_titles or link_key in seen_links:
            continue
        if not art["title"] or not art["link"]:
            continue
        seen_titles.add(title_key)
        seen_links.add(link_key)
        unique.append(art)

    print(f"Total setelah dedup: {len(unique)}")

    # ── Acak urutan → setiap refresh tampil berbeda
    random.shuffle(unique)

    # ── Batasi jumlah total yang dikembalikan
    return unique[:18]


# ═══════════════════════════════════════════════════════════
# TEST (jalankan: python scraper.py)
# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print(" TESTING SCRAPER — 9 SUMBER BERITA")
    print("=" * 60 + "\n")

    news = get_all_news()

    print(f"\n{'=' * 60}")
    print(f" HASIL: {len(news)} BERITA")
    print(f"{'=' * 60}\n")

    for i, item in enumerate(news, 1):
        cat_badge = f"[{item.get('category', '?'):>14}]"
        print(f"[{i:2d}] {cat_badge} [{item['source']:<15}]")
        print(f"     {item['title']}")
        print(f"     Link : {item['link'][:80]}")
        print(f"     Gambar: {'✓' if item['image'] else '✗'}")
        print()
