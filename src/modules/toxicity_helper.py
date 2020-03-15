import requests
import os
import json
from datetime import timedelta

api_key = os.environ["PERSPECTIVE_API"]
TOXIC_THRESHOLD = .80
header = {'Content-type': 'application/json'}
TOXIC = "TOXICITY"
S_TOXIC = "SEVERE_TOXICITY"
IDENTITY = "IDENTITY_ATTACK"
INSULT = "INSULT"
THREAT = "THREAT"
url = 'https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze?key={}'.format(api_key)

def format_json(message):
    """
    Formats the data json to send to the Perspective API
    """
    data = {
        'comment': {'text': message}, 
        'languages': ["en"],
        'requestedAttributes': {
            TOXIC:{}, 
            S_TOXIC: {},
            IDENTITY: {},
            INSULT: {},
            THREAT: {},
            } 
        }
    return json.dumps(data)

def send_format(message, score):
    """
    Formats the embed to send content string
    """
    return  {
                "title": "Message has been marked for toxicity:",
                "color": 53380,
                "fields": [
                    {
                        "name": "Discord Username",
                        "value": message.author.name + "#" + message.author.discriminator
                    },
                    {
                        "name": "Server Nickname",
                        "value": message.author.display_name
                    },
                    {
                        "name": "Time",
                        "value": (message.created_at - timedelta(hours=7))
                    },
                    {
                        "name": "Message",
                        "value": message.clean_content
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
    
    
    
    "Message has been marked for toxicity:\nUser: {}\nChannel: {}\nTime: {}\nMessage: {}\nCertainty: {}".format(
                    message.author.display_name,
                    message.channel.mention,
                    (message.created_at - timedelta(hours=7)),
                    message.clean_content,
                    score*100
                )

def _calculate_heuristic(scores):
    for att, score in scores.items():
        if att != TOXIC:
            if score > TOXIC_THRESHOLD:
                return True
    return False

def _get_toxicity(message_content):
    """
    Helper function for getting the toxicity of a string
    """
    if message_content == "":
        return False, 0
    toxic_json = requests.post(url, headers=header, data=format_json(message_content))
    toxic_json = toxic_json.json()
    scores = {}
    try:
        for attribute in toxic_json['attributeScores']:
            scores[attribute] = toxic_json['attributeScores'][attribute]['summaryScore']['value']

        heuristic = _calculate_heuristic(scores)
        return heuristic, scores
    except Exception as e:
        print(toxic_json)
        print(e)
        return False, scores

def get_toxicity(message):
    """
    Gets the toxicity of a message object and returns the formatted message to send and toxicity score
    """
    is_toxic, scores = _get_toxicity(message.clean_content)
    if is_toxic:
        return send_format(message, scores), scores
    else:
        return None, scores



if __name__ == "__main__":
    print(_get_toxicity("You're a fucking piece of shit"))