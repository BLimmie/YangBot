import unittest
from trigger_class import *


class TriggerTest(unittest.TestCase):
    def test_compile_phrases(self):
        single_phrase = compile_phrases(["foo"])
        self.assertEqual(single_phrase.pattern, r"\b(?:foo)\b")

        multiple_phrases = compile_phrases(["foo", "bar"])
        self.assertEqual(multiple_phrases.pattern, r"\b(?:foo|bar)\b")

        phrase_with_space = compile_phrases(["foo bar"])
        self.assertEqual(phrase_with_space.pattern, r"\b(?:foo\s+bar)\b")

    def test_trigger(self):
        triggers = [
            Trigger(
                pattern=re.compile(r"\btest\b"),
                response="Test Output"
            ),
            Trigger(
                pattern=re.compile(r"\bgauchito\b"),
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
