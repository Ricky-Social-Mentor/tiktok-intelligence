import unittest

from scripts.refresh_news import is_relevant, italian_enough


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

    def test_tiktok_shop_business_topic_is_relevant(self):
        self.assertTrue(is_relevant(
            "TikTok Shop: nuove opportunità per vendere online",
            "Strumenti di vendita e monetizzazione per attività."
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


if __name__ == "__main__":
    unittest.main()
