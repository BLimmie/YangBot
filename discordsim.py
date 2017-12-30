import markovify
from datetime import timedelta

message_cache = 'cached_messages.txt'

SIMULATION_INTERVAL = timedelta(hours=1)
def simulate(filename):
	with open(filename) as file:
		text = file.read()
		markov_model = markovify.NewlineText(text)
		simulation = markov_model.make_sentence(tries=20)
		if simulation is not None:
			return clean_text(simulation)
		else:
			return None


def clean_text(text):
	return text.replace('@', '')
	#This is its own method in case more needs to be cleaned