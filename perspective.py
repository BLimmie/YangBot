import requests
import json
from secretvalues import api_key
#How toxic a message can be before alerting YangBot
#Float between 0 and 1
TOXIC_THRESHOLD = .8
header = {'Content-type': 'application/json'}
url = 'https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze?key={}'.format(api_key)
def format_json(message):
	data = {'comment': {'text': message}, 'requestedAttributes': {'TOXICITY':{}} }
	return json.dumps(data)
def is_toxic(message):
	toxic_json = requests.post(url, headers=header, data=format_json(message))
	toxic_json = toxic_json.json()
	score = toxic_json['attributeScores']['TOXICITY']['summaryScore']['value']
	return score > TOXIC_THRESHOLD

if __name__ == '__main__':
	print(is_toxic('what "kind" of idiot name is foo?'))