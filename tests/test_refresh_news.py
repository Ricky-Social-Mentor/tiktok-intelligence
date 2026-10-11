import unittest

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
