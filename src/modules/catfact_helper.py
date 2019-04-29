import requests

def send_format(catfact):
    return """
    Did you know:
    ```
    {}
    ```
    Type "UNSUBSCRIBE" to unsubscribe from future catfacts.
    """.format(catfact)

def get_catfact():
	response = requests.get("https://catfact.ninja/fact")
	data = response.json()
	return send_format(data['fact'])
    


if __name__ == "__main__":
    print(get_catfact())