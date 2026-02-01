from flask import Flask, jsonify
from flask_cors import CORS
from scraper import get_all_news
import time

app = Flask(__name__)
CORS(app)  # Izinkan request dari domain manapun (termasuk GitHub Pages)

# ─── Simple in-memory cache ───
_cache = {
    "data": [],
    "fetched_at": 0
}
CACHE_TTL = 300  # refresh setiap 5 menit


def get_cached_news():
    now = time.time()
    if now - _cache["fetched_at"] > CACHE_TTL or not _cache["data"]:
        _cache["data"]       = get_all_news(limit_per_source=5)
        _cache["fetched_at"] = now
    return _cache["data"]


# ─── Endpoint utama ───
@app.route("/api/news", methods=["GET"])
def news():
    articles = get_cached_news()
    return jsonify({
        "status" : "ok",
        "count"  : len(articles),
        "cached_at": _cache["fetched_at"],
        "articles": articles
    })


# ─── Health check ───
@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "News Scraper API is running. Use /api/news"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
