import requests

def get_catfact():
	response = requests.get("https://catfact.ninja/fact")
	data = response.json()
	return data['fact']
    


if __name__ == "__main__":
    print(get_catfact())