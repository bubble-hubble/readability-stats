import unittest

from readability import analyze, count_syllables, ease_label, split_sentences


class SyllableTests(unittest.TestCase):
    def test_common_words(self):
        cases = {
            "cat": 1, "the": 1, "make": 1, "table": 2, "water": 2, "happy": 2,
            "jumped": 1, "wanted": 2, "boxes": 2, "beautiful": 3, "radio": 3,
            "university": 5, "don't": 1, "educational": 5, "places": 2,
            "makes": 1, "piano": 3,
        }
        for word, expected in cases.items():
            with self.subTest(word=word):
                self.assertEqual(count_syllables(word), expected)


class SentenceTests(unittest.TestCase):
    def test_split_with_abbreviations(self):
        text = "Dr. Smith arrived. Was he late? No! He was early.\n\nNew paragraph"
        self.assertEqual(len(split_sentences(text)), 5)

    def test_decimal_numbers_do_not_split(self):
        self.assertEqual(len(split_sentences("It costs 3.50 dollars. Cheap.")), 2)


class AnalyzeTests(unittest.TestCase):
    def test_easy_text_scores_easy(self):
        s = analyze("The cat sat on the mat. The dog ran to the park. It was fun.")
        self.assertEqual(s.sentences, 3)
        self.assertEqual(s.words, 15)
        self.assertGreater(s.flesch_reading_ease, 90)
        self.assertLess(s.flesch_kincaid_grade, 3)

    def test_hard_text_scores_hard(self):
        s = analyze(
            "Institutional considerations notwithstanding, the administrative "
            "implementation of comprehensive organizational restructuring "
            "necessitates extraordinarily meticulous interdepartmental coordination."
        )
        self.assertLess(s.flesch_reading_ease, 0)
        self.assertGreater(s.flesch_kincaid_grade, 20)

    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            analyze("  123 ... !!! ")

    def test_labels(self):
        self.assertEqual(ease_label(95), "very easy (5th grade)")
        self.assertEqual(ease_label(10), "very difficult (college graduate)")


if __name__ == "__main__":
    unittest.main()
