import unittest
from html.parser import HTMLParser
from pathlib import Path
import shutil
import subprocess
import tempfile

from scripts.refresh_news import is_relevant, italian_enough, near_duplicate, deduplicate_articles


class RelevanceFilterTests(unittest.TestCase):
    def test_creator_update_is_relevant(self):
        self.assertTrue(is_relevant(
            "TikTok introduce nuove funzioni per i creator",
            "Strumenti per migliorare i contenuti e le visualizzazioni."
        ))

    def test_tiktok_mention_in_unrelated_story_is_not_enough(self):
        self.assertFalse(is_relevant(
            "Le famiglie riducono le spese mensili",
            "Un rapporto cita TikTok solo come esempio secondario."
        ))

    def test_incident_headline_is_excluded(self):
        self.assertFalse(is_relevant(
            "Allarme dopo un incidente legato a TikTok",
            "La notizia descrive un caso di cronaca."
        ))

    def test_tiktok_creator_growth_advice_is_relevant(self):
        self.assertTrue(is_relevant(
            "TikTok: strategie per crescere e migliorare l'engagement",
            "Consigli per creator e contenuti."
        ))

    def test_tiktok_shop_business_topic_is_relevant(self):
        self.assertTrue(is_relevant(
            "TikTok Shop: nuove opportunità per vendere online",
            "Strumenti di vendita e monetizzazione per attività."
        ))

    def test_creator_collaboration_topic_is_relevant(self):
        self.assertTrue(is_relevant(
            "TikTok: nuove collaborazioni tra creator e brand",
            "Opportunità per creator e affiliazioni in Italia."
        ))

    def test_topic_headline_without_tiktok_mention_is_filtered(self):
        self.assertFalse(is_relevant(
            "Esprimiti nei commenti: nuove funzioni Voce, Sondaggi e Caroselli",
            "Nuovi strumenti di community."
        ))

    def test_english_headline_is_filtered(self):
        self.assertFalse(italian_enough(
            "TikTok announces new creator tools and updates",
            "The latest guide for growth and trends."
        ))

    def test_italian_headline_is_kept(self):
        self.assertTrue(italian_enough(
            "TikTok introduce nuovi strumenti per i creator",
            "Ecco come usare le nuove funzioni."
        ))

    def test_near_duplicate_headlines_are_detected(self):
        a = {"title": "TikTok rivoluziona i commenti: arrivano messaggi vocali, sondaggi e foto", "published_at": "2026-09-04T07:00:00Z"}
        b = {"title": "La rivoluzione dei commenti su TikTok: arrivano vocali e sondaggi", "published_at": "2026-09-04T07:00:00Z"}
        self.assertTrue(near_duplicate(a, b))

    def test_syndicated_comment_feature_headlines_are_duplicates(self):
        official = {"title": "Esprimiti nei commenti: ti presentiamo le funzioni Voce, Sondaggi e Caroselli", "published_at": "2026-09-03T07:00:00Z"}
        tgcom = {"title": "TikTok rivoluziona i commenti: arrivano messaggi vocali, sondaggi e foto", "published_at": "2026-09-04T07:00:00Z"}
        report = {"title": "La rivoluzione dei commenti su TikTok: arrivano vocali e sondaggi", "published_at": "2026-09-04T07:00:00Z"}
        self.assertTrue(near_duplicate(official, tgcom))
        self.assertTrue(near_duplicate(official, report))
        self.assertTrue(near_duplicate(tgcom, report))

    def test_different_topics_are_not_duplicates(self):
        a = {"title": "TikTok Shop corso gratuito per giovani creator e imprese", "published_at": "2026-10-09T04:46:06Z"}
        b = {"title": "TikTok: consigli SEO per migliorare la ricerca dei video", "published_at": "2026-10-09T04:46:06Z"}
        self.assertFalse(near_duplicate(a, b))

    def test_deduplication_prefers_official_source(self):
        syndicated = {"title": "TikTok introduce nuove funzioni vocali e sondaggi nei commenti", "published_at": "2026-09-04T07:00:00Z", "url": "https://example.com/story", "confidence": "emerging"}
        official = {"title": "TikTok introduce nuove funzioni vocali e sondaggi nei commenti", "published_at": "2026-09-04T07:00:00Z", "url": "https://newsroom.tiktok.com/story", "confidence": "verified"}
        result = deduplicate_articles([syndicated, official])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["confidence"], "verified")


if __name__ == "__main__":
    unittest.main()


class DashboardScriptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (Path(__file__).resolve().parents[1] / "index.html").read_text(encoding="utf-8")

    def test_saved_example_matching_ignores_generic_terms(self):
        self.assertIn("topicStopWords", self.html)
        self.assertIn("filter(w=>!topicStopWords.has(w))", self.html)

    def test_saved_example_text_uses_real_line_breaks(self):
        self.assertIn(".join('\\n')", self.html)
        self.assertNotIn(".join('\\\\n')", self.html)

    def test_inline_javascript_syntax(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js non disponibile nell'ambiente di test")

        class ScriptParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.in_inline_script = False
                self.current = []
                self.scripts = []

            def handle_starttag(self, tag, attrs):
                if tag == "script" and not dict(attrs).get("src"):
                    self.in_inline_script = True
                    self.current = []

            def handle_data(self, data):
                if self.in_inline_script:
                    self.current.append(data)

            def handle_endtag(self, tag):
                if tag == "script" and self.in_inline_script:
                    code = "".join(self.current).strip()
                    if code:
                        self.scripts.append(code)
                    self.in_inline_script = False
                    self.current = []

        parser = ScriptParser()
        parser.feed(self.html)
        self.assertTrue(parser.scripts, "Nessuno script inline trovato")
        with tempfile.TemporaryDirectory() as tmp:
            for index, code in enumerate(parser.scripts):
                script_path = Path(tmp) / f"inline-{index}.js"
                script_path.write_text(code, encoding="utf-8")
                result = subprocess.run([node, "--check", str(script_path)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
