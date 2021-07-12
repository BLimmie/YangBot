import requests
import random
import discord
import requests
import os
import json
from datetime import timedelta
from modules.toxicity_helper import format_json, _calculate_heuristic
from dotenv import load_dotenv
load_dotenv()

# api_key = os.environ["PERSPECTIVE_API"]
api_key = os.getenv("PERSPECTIVE_API")
TOXIC_THRESHOLD = .87
header = {'Content-type': 'application/json'}
TOXIC = "TOXICITY"
S_TOXIC = "SEVERE_TOXICITY"
IDENTITY = "IDENTITY_ATTACK"
INSULT = "INSULT"
THREAT = "THREAT"
url = 'https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze?key={}'.format(api_key)

# # CATFACT - $catfact
# def send_format(catfact):
#     """
#     Format's the catfact into a the message to send content string
#     """
#     return """
# Thank you for subscribing to CatFacts™
# Did you know:
# ```
# {}```
# Type "UNSUBSCRIBE" to unsubscribe from future catfacts.
#     """.format(catfact)

# def get_catfact():
#     """
#     Gets a catfact from the catfact API
#     """
#     response = requests.get("https://catfact.ninja/fact")
#     data = response.json()
#     return send_format(data['fact'])

# CHOOSE - $choose
def send(option):
    embedVar = discord.Embed(title = ":thinking:", 
                            description = option,
                           color = 53380)
    return "hello".format(embedVar)

def get_choose(message):
    """
    $choose choice1; choice2[; choice3 ....]
    Chooses an option from the list
    """
    content = message.content
    # content = message
    l = " ".join(content.split()[1:])
    opts = l.split("; ")
    if len(opts) < 2 or ";" not in content:
        return "Usage: `$choose choice1; choice2[; choice3...]`"
    
    chosen_opt = opts[random.randint(0,len(opts)-1)]
    return send(chosen_opt)
    
# TOXICITY CHECK
# def format_json(message):
#     """
#     Formats the data json to send to the Perspective API
#     """
#     data = {
#         'comment': {'text': message}, 
#         'languages': ["en"],
#         'requestedAttributes': {
#             TOXIC:{}, 
#             S_TOXIC: {},
#             IDENTITY: {},
#             INSULT: {},
#             THREAT: {},
#             } 
#         }
#     return json.dumps(data)

def send_format2(message, score):
    """
    Formats the embed to send content string
    """

    embedVar2 = {
                "title": "Message has been marked for toxicity:",
                "color": 53380,
                "fields": [
                    {
                        "name": "Discord Username",
                        "value": 'message.author.name' + "#" + 'message.author.discriminator'
                    },
                    {
                        "name": "Server Nickname",
                        "value": 'message.author.display_name'
                    },
                    {
                        "name": "Time",
                        "value": '(message.created_at - timedelta(hours=7))'
                    },
                    {
                        "name": "Message",
                        "value": 'message.clean_content'
                    },
                    {
                        "name": "Toxic",
                        "value": score[TOXIC],
                        "inline": True
                    },
                    {
                        "name": "Severely Toxic",
                        "value": score[S_TOXIC],
                        "inline": True
                    },
                    {
                        "name": "Attack on Identity",
                        "value": score[IDENTITY],
                        "inline": True
                    },
                    {
                        "name": "Insult",
                        "value": score[INSULT],
                        "inline": True
                    },
                    {
                        "name": "Threat",
                        "value": score[THREAT],
                        "inline": True
                    }
                ]
                }
    return  "what".format(embedVar2)
    
    
    
    "Message has been marked for toxicity:\nUser: {}\nChannel: {}\nTime: {}\nMessage: {}\nCertainty: {}".format(
                    message.author.display_name,
                    message.channel.mention,
                    (message.created_at - timedelta(hours=7)),
                    message.clean_content,
                    score*100
                )

# def _calculate_heuristic(scores):
#     for att, score in scores.items():
#         if att != TOXIC:
#             if score > TOXIC_THRESHOLD:
#                 return True
#     return False

def _get_toxicity(message_content, scores):
    """
    Helper function for getting the toxicity of a string
    """
    if message_content == "":
        return False, 0
    toxic_json = requests.post(url, headers=header, data=format_json(message_content))
    # response = toxic_json
    toxic_json = toxic_json.json()
    # if response.ok:
    #     return response.text
    # else:
    #     return 'Bad Response!'
    # scores = {}
    try:
        # for attribute in toxic_json['attributeScores']:
        #     scores[attribute] = toxic_json['attributeScores'][attribute]['summaryScore']['value']

        heuristic = _calculate_heuristic(scores)
        return heuristic, scores
    except Exception as e:
        # print(toxic_json)
        print(e)
        return False, scores

def get_toxicity(message, scores2):
    """
    Gets the toxicity of a message object and returns the formatted message to send and toxicity score
    """
    # is_toxic, scores = _get_toxicity(message.clean_content)
    is_toxic, scores = _get_toxicity(message, scores2)
    if is_toxic:
        return send_format2(message, scores), scores
    else:
        return None, scores

    
# if __name__ == "__main__":
#     # print(get_catfact())
#     print('hello') # function should be printed? choose
#     print(_get_toxicity("You're a fucking piece of shit"))