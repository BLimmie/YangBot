from modules.catfact_helper import send_format, get_catfact
import unittest
from modules.test import get_choose, get_toxicity, _get_toxicity, _calculate_heuristic, send_format2, send, format_json
import json

TOXIC = "TOXICITY"
S_TOXIC = "SEVERE_TOXICITY"
IDENTITY = "IDENTITY_ATTACK"
INSULT = "INSULT"
THREAT = "THREAT"
scores = {
            TOXIC: 0, 
            S_TOXIC: 0,
            IDENTITY: 0,
            INSULT: 0,
            THREAT: 0,
            }
toxic_scores = {
            TOXIC: 0.9, 
            S_TOXIC: 0.9,
            IDENTITY: 0.9,
            INSULT: 0.9,
            THREAT: 0.9,
            }

mix_scores = {
            TOXIC: 0.87, 
            S_TOXIC: 0.5,
            IDENTITY: 0.9,
            INSULT: 0.9,
            THREAT: 0.9,
            }

# CAT FACT- $catfact
class TestCatFact(unittest.TestCase):
    # get_catfact()
    def test_catfact(self):
        # self.assertIn(Expected Result, Function)
        self.assertIn("Thank you for subscribing to CatFacts™", get_catfact())

    # send_format in catfact_helper
    def test_send_format(self):
        self.assertIn("Thank you for subscribing to CatFacts™", send_format('catfact'))

# CHOOSE- $choose
class TestChoose(unittest.TestCase):
    # get_choose(message)
    def test_choose(self):
        # $choose x; y; z
        self.assertIn("hello", get_choose('$choose x; y; z'))
        # Empty $choose
        self.assertIn("Usage: `$choose choice1; choice2[; choice3...]`", get_choose('$choose'))

    # send(option)
    def test_send(self):
        self.assertIn("hello", send('x'))

# TOXICITY CHECK
class TestToxicityCheck(unittest.TestCase):
    # send_format2 in toxicity_helper
    def test_send_format2(self):
        # All Toxic Scores
        self.assertEqual("what", send_format2("bitch U MAKE THE BURRITO", toxic_scores))
        # Mixed Scores Toxic & Non-Toxic
        self.assertEqual("what", send_format2("bitch U MAKE THE BURRITO", mix_scores))
        # All Non-Toxic Scores
        self.assertEqual("what", send_format2("hello", scores))
        
    # format_json(message)
    def test_format_json(self):
        data = {
        'comment': {'text': 'message'}, 
        'languages': ["en"],
        'requestedAttributes': {
            TOXIC: {}, 
            S_TOXIC: {},
            IDENTITY: {},
            INSULT: {},
            THREAT: {},
            } 
        }
        self.assertEqual(json.dumps(data), format_json('message'))
    
    # _calculate_heuristic(scores)
    def test_calculate_heuristic(self):
        # Toxic Heuristic Check for All Toxic Scores
        self.assertTrue(_calculate_heuristic(toxic_scores))        # self.assertTrue(function)
        # Toxic Heuristic Check for Mixed Scores
        self.assertTrue(_calculate_heuristic(mix_scores))        # self.assertTrue(function)
        # Non-Toxic Heuristic Check for All Non-Toxic Scores
        self.assertFalse(_calculate_heuristic(scores))        # self.assertFalse(function)

    # _get_toxicity(message_content)
    def test_get_toxicity(self):
        # message_content == "" is False
        # All Toxic Scores
        self.assertFalse(False, _get_toxicity('', toxic_scores))
        # Mixed Scores Toxic & Non-Toxic
        self.assertFalse(False, _get_toxicity('', mix_scores))
        # All Non-Toxic Scores
        self.assertFalse(False, _get_toxicity('', scores))

        # message_content == "" is True
        # Try
        # All Toxic Scores
        self.assertEqual((_calculate_heuristic(toxic_scores), toxic_scores), _get_toxicity("bitch U MAKE THE BURRITO", toxic_scores))
        # Mixed Scores Toxic & Non-Toxic
        self.assertEqual((_calculate_heuristic(mix_scores), mix_scores), _get_toxicity("bitch U MAKE THE BURRITO", mix_scores))
        # All Non-Toxic Scores
        self.assertEqual((_calculate_heuristic(scores), scores), _get_toxicity("bitch U MAKE THE BURRITO", scores))
        # Exception
        with self.assertRaises(NameError):
            _get_toxicity(jcnqejc, {})

    # get_toxicity(message)
    def test_toxicity(self):
        # Toxic Check for All Toxic Scores: "bitch U MAKE THE BURRITO" 
        self.assertEqual((send_format2('bitch U MAKE THE BURRITO', toxic_scores), toxic_scores), get_toxicity('bitch U MAKE THE BURRITO', toxic_scores))
        # Toxic Check for Mixed Scores: "bitch U MAKE THE BURRITO" 
        self.assertEqual((send_format2('bitch U MAKE THE BURRITO', mix_scores), mix_scores), get_toxicity('bitch U MAKE THE BURRITO', mix_scores))
        # Non-Toxic Check: "hello"
        self.assertEqual((None, {}), get_toxicity('hello', {}))

        

if __name__ == '__main__':
    unittest.main()

    # def __init__(self, function): 
    #     """
    #     Initialization of all data and functions of unit test
    #     """

    # def __call__(self):
    #     return True