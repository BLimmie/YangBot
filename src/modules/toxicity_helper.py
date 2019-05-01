import requests
import os
import json
from datetime import timedelta

api_key = os.environ["PERSPECTIVE_API"]
TOXIC_THRESHOLD = .83
header = {'Content-type': 'application/json'}

url = 'https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze?key={}'.format(api_key)

def format_json(message):
    data = {'comment': {'text': message}, 'languages': ["en"],'requestedAttributes': {'TOXICITY':{}, 'SEVERE_TOXICITY': {}} }
    return json.dumps(data)

def send_format(message, score):
    return  "Message has been marked for toxicity:\nUser: {}\nChannel: {}\nTime: {}\nMessage: {}\nCertainty: {}".format(
                    message.author.display_name, 
                    message.channel.mention, 
                    (message.created_at - timedelta(hours=7)), 
                    message.clean_content, 
                    score*100
                )

def _get_toxicity(message_content):
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
    Pass a message, not a string
    """
    is_toxic, score = _get_toxicity(message.clean_content)
    if is_toxic:
        return send_format(message, score), score
    else:
        return None
    


if __name__ == "__main__":
    print(_get_toxicity("You're a fucking piece of shit"))