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
    ("Trucchi e crescita", 'consigli TikTok creator crescere algoritmo contenuti strategie'),
    ("Trend e creator", 'tendenze TikTok creator virale Italia trend 2026 when:30d'),
    ("Strategia contenuti", 'TikTok consigli creator hook storytelling SEO engagement Italia 2026 when:30d'),
    ("Creator e strumenti", 'TikTok creator strumenti video commenti caroselli sondaggi Italia'),
    ("Crescita pratica", 'TikTok come aumentare visualizzazioni completamento video creator Italia when:30d'),
    ("Monetizzazione", 'TikTok creator monetizzazione collaborazioni affiliazione Italia'),
    ("Guide social", 'site:socialmediatoday.com TikTok creator video marketing'),
    ("Creator marketing", 'site:later.com/blog TikTok creator tips trends'),
    ("TikTok ufficiale", 'site:newsroom.tiktok.com/it-IT TikTok creator strumenti contenuti'),
    ("IA e strumenti ufficiali", 'site:newsroom.tiktok.com/it-IT TikTok IA inserzionisti strumenti campagne creator 2026'),
    ("Vendita e business", 'TikTok Shop vendere aziende piccole attività Italia'),
    ("TikTok Shop ufficiale", 'site:seller-it.tiktok.com/university TikTok Shop creator Italia'),
    ("Creator italiani", 'TikTok creator italiani consigli contenuti strategie social media'),
    ("Video e retention", 'TikTok durata video retention completamento visualizzazioni creator Italia when:30d'),
    ("Ricerca TikTok", 'TikTok SEO ricerca parole chiave caption hashtag creator Italia when:30d'),
    ("Brand e partnership", 'TikTok influencer marketing campagne brand creator Italia'),
    ("Strumenti per video", 'TikTok editor video sottotitoli montaggio creator Italia'),
    ("Community e commenti", 'TikTok community commenti risposte creator nuove funzioni Italia'),
    ("Trend social italiani", 'TikTok trend audio format creator social media Italia questa settimana when:30d'),
    ("Creator economy", 'TikTok economia creator guadagnare collaborazioni Italia'),
    ("Fonti social italiane", 'site: punto-informatico.it TikTok creator aggiornamento'),
    ("Marketing digitale", 'site: ninja.it TikTok creator social media marketing'),
    ("Creator e formazione", 'site: engage.it TikTok creator influencer marketing'),
]
OFFICIAL_DOMAINS = ("newsroom.tiktok.com", "news.tiktok.com")
# Segnali distinti: una semplice menzione di TikTok nella descrizione non basta.
TITLE_RELEVANCE_MARKERS = (
    "tiktok shop", "creator economy", "creator", "creatori",
    "algoritmo", "funzione", "funzioni", "aggiornamento", "aggiornamenti",
    "strumenti", "contenuti", "visualizzazioni", "follower", "hashtag",
    "monetizzazione", "diretta", "live shopping", "trend", "tendenze",
    "marketing", "pubblicità", "sondaggi", "caroselli", "crescere",
    "crescita", "strategie", "strategia", "consigli", "tutorial",
    "engagement", "seo", "hook", "storytelling", "pubblicare",
    "visualizzazioni", "completamento", "collaborazioni", "affiliazione",
    "affiliazioni", "brand", "sondaggi", "caroselli", "commenti",
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
    # Documenti amministrativi e annunci di lavoro non aiutano direttamente
    # a creare video, crescere come creator o sviluppare una strategia social.
    "termini di servizio", "politica sui contenuti", "politica sulle recensioni",
    "stipendio", "laureati", "senza esperienza", "offerte di lavoro",
    "annuncio di lavoro", "annunci di lavoro", "assume laureati",
    "recensioni dei clienti importate", "recensioni importate",
    "dichiarazione di tiktok shop sulle recensioni",
)
HEADERS = {"User-Agent": "TikTokIntelligence/1.1 (public RSS reader)"}
MAX_AGE_DAYS = 90
ITALIAN_MARKERS = {"il", "lo", "la", "gli", "le", "un", "una", "di", "del", "della", "dei", "delle", "che", "per", "con", "su", "come", "nuovo", "nuova", "nuove", "aggiornamento", "funzioni", "creator", "tiktok", "sono", "arriva", "arrivano", "dopo", "dalle", "dalla", "anche", "più", "italia", "italiano", "italiana", "video", "commenti", "strumenti"}
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
    has_tiktok_mention = "tiktok" in full_text
    title_has_signal = any(marker in title_text for marker in TITLE_RELEVANCE_MARKERS)
    topic_hits = sum(1 for marker in TOPIC_MARKERS if marker in full_text)
    # Servono sia un riferimento esplicito a TikTok sia un tema utile ai creator nel titolo.
    return has_tiktok_mention and title_has_signal and topic_hits >= 1

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

def title_tokens(title):
    stop = {"tiktok", "tik", "tok", "nuove", "nuovi", "nuova", "nuovo", "arriva", "arrivano", "per", "con", "della", "delle", "degli", "dei", "come", "sul", "sulla", "nel", "nella", "il", "lo", "la", "i", "gli", "le", "un", "una", "di", "e", "a", "da", "in", "su"}
    return {word for word in re.findall(r"[a-zà-ÿ0-9]+", title.lower()) if len(word) > 2 and word not in stop}

def near_duplicate(a, b):
    """Confronta titoli normalizzati per evitare versioni quasi identiche della stessa notizia."""
    ta, tb = title_tokens(a.get("title", "")), title_tokens(b.get("title", ""))
    if not ta or not tb:
        return False
    intersection = len(ta & tb)
    jaccard = intersection / len(ta | tb)
    containment = intersection / min(len(ta), len(tb))
    if jaccard < 0.40 and containment < 0.65:
        # Riconosce le diverse formulazioni della stessa notizia sulle funzioni
        # dei commenti, senza confondere articoli su argomenti differenti.
        shared = ta & tb
        comment_feature_terms = {"commenti"} & shared
        feature_terms = {"vocali", "vocale", "voce", "sondaggi", "caroselli", "carosello", "foto", "fotografie"}
        if not comment_feature_terms or len(shared & feature_terms) == 0:
            return False
    try:
        da = datetime.fromisoformat(a["published_at"].replace("Z", "+00:00"))
        db = datetime.fromisoformat(b["published_at"].replace("Z", "+00:00"))
        return abs((da - db).total_seconds()) <= 14 * 86400
    except (KeyError, ValueError, TypeError):
        return False

def deduplicate_articles(items):
    """Deduplica URL esatti e titoli simili, preferendo fonti ufficiali a parità di data."""
    ranked = sorted(
        items,
        key=lambda a: (
            a.get("confidence") == "verified",
            a.get("published_at") or "",
            bool(a.get("summary")),
        ),
        reverse=True,
    )
    kept, seen_urls = [], set()
    for item in ranked:
        url = item.get("url", "").split("?")[0].rstrip("/")
        if not url or url in seen_urls:
            continue
        if any(near_duplicate(item, existing) for existing in kept):
            continue
        seen_urls.add(url)
        kept.append(item)
    return sorted(kept, key=lambda a: a.get("published_at") or "", reverse=True)

def main():
    items, errors = [], []
    for category, query in QUERIES:
        try:
            items.extend(fetch(query, category))
        except Exception as exc:
            errors.append(f"{category}: {type(exc).__name__}")
    unique = deduplicate_articles(items)
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
