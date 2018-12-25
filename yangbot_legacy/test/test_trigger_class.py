import unittest
from trigger_class import *


class TriggerTest(unittest.TestCase):
    def test_match_phrases(self):
        single_phrase = match_phrases(["foo"])
        self.assertEqual(single_phrase._source.pattern, r"\b(?:foo)\b")

        multiple_phrases = match_phrases(["foo", "bar"])
        self.assertEqual(multiple_phrases._source.pattern, r"\b(?:foo|bar)\b")

        phrase_with_space = match_phrases(["foo bar"])
        self.assertEqual(phrase_with_space._source.pattern, r"\b(?:foo\s+bar)\b")

    def test_trigger(self):
        test_regex = re.compile(r"\btest\b")
        gauchito_regex = re.compile(r"\bgauchito\b")
        triggers = [
            Trigger(
                predicate=(lambda x: test_regex.search(x) is not None),
                response="Test Output"
            ),
            Trigger(
                predicate=(lambda x: gauchito_regex.search(x) is not None),
                response="Gauchito Output",
                gauchito_only=True
            )
        ]

        self.assertEqual(find_response(
            triggers=triggers,
            message="This is a test",
            is_gauchito=False
        ), "Test Output")

        self.assertEqual(find_response(
            triggers=triggers,
            message="This is a test",
            is_gauchito=True
        ), "Test Output")

        self.assertEqual(find_response(
            triggers=triggers,
            message="Am I a gauchito?",
            is_gauchito=True
        ), "Gauchito Output")

        self.assertIsNone(find_response(
            triggers=triggers,
            message="Am I a gauchito?",
            is_gauchito=False
        ))

        self.assertIsNone(find_response(
            triggers=triggers,
            message="I match no triggers",
            is_gauchito=False
        ))

        self.assertIsNone(find_response(
            triggers=triggers,
            message="I match no triggers",
            is_gauchito=True
        ))


if __name__ == "__main__":
    unittest.main()
