from discord import channel
from modules.catfact_helper import send_format, get_catfact
from modules.toxicity_helper import format_json, _calculate_heuristic, get_toxicity, _get_toxicity
from modules.toxicity_helper import send_format as send_format2
import unittest
import json
from tools.message_return import message_data
import datetime
from access_dict_by_dot import AccessDictByDot

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


# class Message:
#     def __init__(self, content = None, channel = None):
#         self.content = content if not None else None
#         self.channel = channel if not None else None
#         self.created_at = datetime.datetime(2021, 8, 11, 14, 24, 29, 716000)
#     class author:
#         def __init__(self):
#             self.name = 'name'
#             self.discriminator = 'discriminator' 
#             self.display_name = 'display_name' 
#             self.clean_content = 'clean_content'

bad_message = {
    'content':'bitch U MAKE THE BURRITO',
    'channel':'channel',
    'created_at': datetime.datetime(2021, 8, 11, 14, 24, 29, 716000),
    'clean_content':'bitch U MAKE THE BURRITO',
    'author':{
                'name':'name',
                'discriminator':'discriminator',
                'display_name':'display_name'
            }
        }

good_message = {
    'content':'hello',
    'channel':'channel',
    'created_at': datetime.datetime(2021, 8, 11, 14, 24, 29, 716000),
    'clean_content':'clean_content',
    'author':{
                'name':'name',
                'discriminator':'discriminator',
                'display_name':'display_name'
            }
        }

message = {'channel':'dev-testing'}

bad = AccessDictByDot.load(bad_message)
good = AccessDictByDot.load(good_message)
fact = AccessDictByDot.load(message)

# CAT FACT- $catfact
class TestCatFact(unittest.TestCase):
    # get_catfact()
    def test_catfact(self):
        # self.assertIn(Expected Result, Function)
        self.assertIn("Thank you for subscribing to CatFacts™", get_catfact())

    # send_format in catfact_helper
    def test_send_format(self):
        self.assertIn("Thank you for subscribing to CatFacts™", send_format('catfact'))

    # message_data
    def test_message_data(self):
        self.assertIsInstance(message_data('dev-testing', get_catfact()), message_data)

# CHOOSE- $choose
class TestChoose(unittest.TestCase):
    # get_choose(message)
    def test_choose(self):
        # $choose x; y; z
        # self.assertIn("hello", get_choose(Message('$choose x; y; z')))
        data = message_data(
            channel='dev-testing',
            message="",
            embed={
                "title": ":thinking:",
                "description": 'x',
                "color": 53380}
        )
        self.assertEqual("", data.message)
        # Empty $choose
        # self.assertIn("Usage: `$choose choice1; choice2[; choice3...]`", get_choose(Message('$choose')))
        empty = message_data(
                channel='dev-testing',
                message= "Usage: `$choose choice1; choice2[; choice3...]`"
            )
        self.assertEqual("Usage: `$choose choice1; choice2[; choice3...]`", empty.message)

    # message_data- $choose x; y; z
    def test_message_data(self):
        self.assertIsInstance(message_data(
            channel='dev-testing',
            message = "", 
            embed = {
                "title": ":thinking:",
                "description": 'x',
                "color": 53380
            }
        ), message_data)

    # message_data- Empty $choose
    def test_message_data_empty(self):
        self.assertIsInstance(message_data(
                channel='dev-testing',
                message= "Usage: `$choose choice1; choice2[; choice3...]`"
            ), message_data)

# TOXICITY CHECK
class TestToxicityCheck(unittest.TestCase):
    # send_format2 in toxicity_helper
    def test_send_format2(self):
        # All Toxic Scores
        self.assertIn("title", send_format2(bad, toxic_scores).keys())
        # Mixed Scores Toxic & Non-Toxic
        self.assertIn("title", send_format2(bad, mix_scores).keys())
        # All Non-Toxic Scores
        self.assertIn("title", send_format2(good, scores).keys())

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
        self.assertTrue(_calculate_heuristic(mix_scores))          # self.assertTrue(function)
        # Non-Toxic Heuristic Check for All Non-Toxic Scores
        self.assertFalse(_calculate_heuristic(scores))             # self.assertFalse(function)

    # _get_toxicity(message_content)
    def test_get_toxicity(self):
        # message content Empty
        self.assertFalse(False, _get_toxicity(''))

        # Toxic Check: "bitch U MAKE THE BURRITO" 
        self.assertTrue(True, _get_toxicity(bad.content))
        # Non-Toxic Check: "hello"
        self.assertFalse(False, _get_toxicity(good.content))

        # Exception- inserting an int instead of string
        self.assertFalse(False, _get_toxicity(1))

    # get_toxicity(message)
    def test_toxicity(self):
        # Toxic Check: - checks both elements in tuple- send_format and scores
        # Toxic Check Passed
        if 'title' in get_toxicity(bad)[0].keys() and 'TOXICITY' in get_toxicity(bad)[1].keys(): 
            self.assertIsNone(None, get_toxicity(good))
        # Toxic Check Failed
        else:
            self.assertIsNotNone(None, get_toxicity(good))
            
        # Non-Toxic Check: "hello"
        self.assertIsNone(None, get_toxicity(good))

if __name__ == '__main__':
    unittest.main()