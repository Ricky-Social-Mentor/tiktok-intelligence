#!/usr/bin/env python3
"""Raccoglie notizie TikTok in italiano da feed RSS pubblici."""
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
from html import unescape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "news.json"
# Query in italiano e categorie distinte per rendere il feed più leggibile.
QUERIES = [
    ("Funzioni TikTok", 'site:newsroom.tiktok.com/it-IT OR site:newsroom.tiktok.com "funzione" OR "strumenti" TikTok'),
    ("Aggiornamenti TikTok", 'TikTok aggiornamento novità piattaforma Italia'),
    ("Trucchi e crescita", 'consigli TikTok creator crescere algoritmo contenuti'),
    ("Trend e creator", 'tendenze TikTok creator virale Italia'),
    ("Vendita e business", 'TikTok Shop vendere aziende piccole attività Italia'),
]
OFFICIAL_DOMAINS = ("newsroom.tiktok.com", "news.tiktok.com")
# Segnali distinti: una semplice menzione di TikTok nella descrizione non basta.
TITLE_RELEVANCE_MARKERS = (
    "tiktok", "tik tok", "tiktok shop", "creator economy",
    "creator", "creatori", "social media", "social network",
    "video brevi", "short video", "reels", "reel",
)
TOPIC_MARKERS = (
    "funzione", "funzioni", "aggiornamento", "aggiornamenti", "novità",
    "strumenti", "algoritmo", "contenuti", "video", "visualizzazioni",
    "follower", "community", "diretta", "live shopping", "vendere",
    "monetizzazione", "creator", "creatori", "social", "trend", "tiktok",
)
OFF_TOPIC_MARKERS = (
    "autolesion", "omicidio", "arrestat", "polizia", "incidente",
    "insultano", "insulto", "allarme", "tragedia", "morto", "morta",
)
HEADERS = {"User-Agent": "TikTokIntelligence/1.1 (public RSS reader)"}
MAX_AGE_DAYS = 60
ITALIAN_MARKERS = {"il", "lo", "la", "gli", "le", "un", "una", "di", "del", "della", "dei", "delle", "che", "per", "con", "su", "come", "nuovo", "nuova", "nuove", "aggiornamento", "funzioni", "creator", "tiktok"}
ENGLISH_MARKERS = {"the", "and", "for", "with", "from", "how", "what", "why", "new", "latest", "tips", "guide", "trend", "trends", "households", "returning", "levels", "lead", "exclusive", "announces", "introduces", "update", "updates", "growth", "small", "business", "viral"}

def clean(value):
    value = unescape(re.sub(r"<[^>]+>", " ", value or ""))
    return re.sub(r"\s+", " ", value).strip()

def parse_date(value):
    try:
        dt = parsedate_to_datetime(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None

def italian_enough(title, summary):
    words = set(re.findall(r"[a-zà-ÿ]+", (title + " " + summary).lower()))
    it_score = len(words & ITALIAN_MARKERS)
    en_score = len(words & ENGLISH_MARKERS)
    # Titles mostly in English are excluded instead of shown untranslated.
    return not (en_score >= 2 and en_score > it_score)

def is_relevant(title, summary):
    title_text = title.lower().replace("tik tok", "tiktok")
    full_text = (title + " " + summary).lower().replace("tik tok", "tiktok")
    # Scarta titoli di cronaca non utili a creare contenuti, anche se citano TikTok.
    if any(marker in title_text for marker in OFF_TOPIC_MARKERS):
        return False
    title_has_signal = any(marker in title_text for marker in TITLE_RELEVANCE_MARKERS)
    topic_hits = sum(1 for marker in TOPIC_MARKERS if marker in full_text)
    # La pertinenza deve emergere soprattutto dal titolo, oppure da più segnali tematici.
    return title_has_signal and topic_hits >= 1

def fetch(query, category):
    params = urllib.parse.urlencode({"q": query, "hl": "it", "gl": "IT", "ceid": "IT:it"})
    url = "https://news.google.com/rss/search?" + params
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=25) as response:
        root = ET.fromstring(response.read())
    found = []
    now = datetime.now(timezone.utc)
    for item in root.findall("./channel/item"):
        title = clean(item.findtext("title", ""))
        link = (item.findtext("link", "") or "").strip()
        desc = clean(item.findtext("description", ""))
        source_el = item.find("source")
        source = clean(source_el.text if source_el is not None else "Google News")
        source_url = (source_el.attrib.get("url", "") if source_el is not None else "").strip()
        source_host = urllib.parse.urlparse(source_url).netloc.lower()
        published = parse_date(item.findtext("pubDate", ""))
        if not title or not link or not published:
            continue
        if published < now - timedelta(days=MAX_AGE_DAYS) or published > now + timedelta(days=1):
            continue
        if not italian_enough(title, desc) or not is_relevant(title, desc):
            continue
        verified = any(source_host == domain or source_host.endswith("." + domain) for domain in OFFICIAL_DOMAINS)
        found.append({
            "id": re.sub(r"[^a-z0-9]+", "-", (link + title).lower()).strip("-")[:100],
            "title": title,
            "summary": desc[:360],
            "url": link,
            "source": source,
            "source_url": source_url,
            "category": category,
            "confidence": "verified" if verified else "emerging",
            "published_at": published.isoformat(timespec="seconds").replace("+00:00", "Z"),
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
    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "articles": unique[:50],
        "source_note": "Feed in italiano, limitato a contenuti recenti; apri la fonte originale per verificare i dettagli.",
        "collection_warnings": errors,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(payload['articles'])} Italian recent articles; feed errors: {len(errors)}")

if __name__ == "__main__":
    main()
