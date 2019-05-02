import requests

def send_format(catfact):
    """
    Format's the catfact into a the message to send content string
    """
    return """
Thank you for subscribing to CatFacts™
Did you know:
```
{}```
Type "UNSUBSCRIBE" to unsubscribe from future catfacts.
    """.format(catfact)

def get_catfact():
    """
    Gets a catfact from the catfact API
    """
    response = requests.get("https://catfact.ninja/fact")
    data = response.json()
    return send_format(data['fact'])



if __name__ == "__main__":
    print(get_catfact())