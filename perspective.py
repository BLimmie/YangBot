import json

import requests

from secretvalues import api_key

# How toxic a message can be before alerting YangBot
# Float between 0 and 1
TOXIC_THRESHOLD = .83
header = {'Content-type': 'application/json'}
url = 'https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze?key={}'.format(api_key)


def format_json(message):
    data = {'comment': {'text': message}, 'languages': ["en"],
            'requestedAttributes': {'TOXICITY': {}, 'SEVERE_TOXICITY': {}}}
    return json.dumps(data)


def is_toxic(message):
    toxic_json = requests.post(url, headers=header, data=format_json(message))
    toxic_json = toxic_json.json()
    try:
        score = toxic_json['attributeScores']['SEVERE_TOXICITY']['summaryScore']['value']
        return (score > TOXIC_THRESHOLD), score
    except Exception as e:
        print(toxic_json)


if __name__ == '__main__':
    print(is_toxic('I can do ur makeup n shiet'))
