import unittest

from fek_to_md.converter import clean_text, structure_markdown


class ConverterTextTests(unittest.TestCase):
    def test_clean_text_joins_greek_hyphenated_words(self):
        self.assertEqual(clean_text("περιλαμ-\nβανόμενο"), "περιλαμβανόμενο")

    def test_clean_text_preserves_article_line(self):
        text = clean_text("Αυτό είναι εισαγωγικό\nΆρθρο 1\nΚείμενο")
        self.assertIn("εισαγωγικό\nΆρθρο 1", text)

    def test_structure_markdown_adds_article_and_paragraph_headings(self):
        text = structure_markdown("Άρθρο 2\n1. Το παρόν εφαρμόζεται.")
        self.assertIn("## Άρθρο 2", text)
        self.assertIn("### Παράγραφος 1\nΤο παρόν εφαρμόζεται.", text)


if __name__ == "__main__":
    unittest.main()
