#!/usr/bin/env python3
"""Collect a small set of public Google News RSS searches into news.json."""
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from html import unescape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "news.json"
QUERIES = [
    ("Novità TikTok", 'site:newsroom.tiktok.com TikTok'),
    ("Algoritmo e crescita", 'TikTok algorithm creator tips growth'),
    ("Trend e creator", 'TikTok trends creators viral trend'),
    ("Vendita e business", 'TikTok Shop social commerce small business'),
]
OFFICIAL_DOMAINS = ("newsroom.tiktok.com", "newsroom.tiktok.com/en-us", "news.tiktok.com")
HEADERS = {"User-Agent": "TikTokIntelligence/1.0 (public RSS reader)"}

def clean(value):
    value = unescape(re.sub(r"<[^>]+>", " ", value or ""))
    return re.sub(r"\\s+", " ", value).strip()

def parse_date(value):
    try:
        dt = parsedate_to_datetime(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    except Exception:
        return None

def fetch(query, category):
    params = urllib.parse.urlencode({"q": query, "hl": "it", "gl": "IT", "ceid": "IT:it"})
    url = "https://news.google.com/rss/search?" + params
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as response:
        data = response.read()
    root = ET.fromstring(data)
    found = []
    for item in root.findall("./channel/item"):
        title = clean(item.findtext("title", ""))
        link = (item.findtext("link", "") or "").strip()
        desc = clean(item.findtext("description", ""))
        source_el = item.find("source")
        source = clean(source_el.text if source_el is not None else "Google News")
        pub = parse_date(item.findtext("pubDate", ""))
        if not title or not link:
            continue
        host = urllib.parse.urlparse(link).netloc.lower()
        verified = any(domain in host for domain in OFFICIAL_DOMAINS)
        found.append({
            "id": re.sub(r"[^a-z0-9]+", "-", (link + title).lower()).strip("-")[:100],
            "title": title,
            "summary": desc[:520],
            "url": link,
            "source": source,
            "category": category,
            "confidence": "verified" if verified else "emerging",
            "published_at": pub,
        })
    return found

def main():
    items, errors = [], []
    for category, query in QUERIES:
        try:
            items.extend(fetch(query, category))
        except Exception as exc:
            errors.append(f"{category}: {type(exc).__name__}")
    unique, seen = [], set()
    for item in sorted(items, key=lambda a: a.get("published_at") or "", reverse=True):
        key = item["url"]
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    # Keep a manageable, recent list; feeds may include older stories if results are sparse.
    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "articles": unique[:60],
        "source_note": "Public RSS search results. Verify the linked original source before publishing claims.",
        "collection_warnings": errors,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
    print(f"Wrote {len(payload['articles'])} articles; feed errors: {len(errors)}")

if __name__ == "__main__":
    main()
