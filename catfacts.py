import requests

def get_random_catfact():
	response = requests.get("https://catfact.ninja/fact")
	data = response.json()
	return data['fact']

