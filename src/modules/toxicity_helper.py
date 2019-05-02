import requests
import os
import json
from datetime import timedelta

api_key = os.environ["PERSPECTIVE_API"]
TOXIC_THRESHOLD = .83
header = {'Content-type': 'application/json'}

url = 'https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze?key={}'.format(api_key)

def format_json(message):
    """
    Formats the data json to send to the Perspective API
    """
    data = {'comment': {'text': message}, 'languages': ["en"],'requestedAttributes': {'TOXICITY':{}, 'SEVERE_TOXICITY': {}} }
    return json.dumps(data)

def send_format(message, score):
    """
    Formats the message to send content string
    """
    return  "Message has been marked for toxicity:\nUser: {}\nChannel: {}\nTime: {}\nMessage: {}\nCertainty: {}".format(
                    message.author.display_name,
                    message.channel.mention,
                    (message.created_at - timedelta(hours=7)),
                    message.clean_content,
                    score*100
                )

def _get_toxicity(message_content):
    """
    Helper function for getting the toxicity of a string
    """
    toxic_json = requests.post(url, headers=header, data=format_json(message_content))
    toxic_json = toxic_json.json()
    try:
        score = toxic_json['attributeScores']['SEVERE_TOXICITY']['summaryScore']['value']
        return (score > TOXIC_THRESHOLD), score
    except Exception as e:
        print(toxic_json)
        return False, score

def get_toxicity(message):
    """
    Gets the toxicity of a message object and returns the formatted message to send and toxicity score
    """
    is_toxic, score = _get_toxicity(message.clean_content)
    if is_toxic:
        return send_format(message, score), score
    else:
        return None, score



if __name__ == "__main__":
    print(_get_toxicity("You're a fucking piece of shit"))