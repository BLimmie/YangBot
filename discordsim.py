import markovify
from datetime import timedelta

message_cache = 'cached_messages.txt'
email_sim = 'emails.txt'
email_model = markovify.Text(open('emails.txt').read())
print('Markov Model loaded')
SIMULATION_INTERVAL = timedelta(hours=1)
def simulate(filename, test=True, nl=True):
	with open(filename) as file:
		if nl:
			text = file.read()
			markov_model = markovify.NewlineText(text)
		else:
			markov_model = email_model
		simulation = markov_model.make_sentence(test_output=test)
		if simulation is not None:
			return clean_text(simulation)
		else:
			return None


def clean_text(text):
	return text.replace('@', '')
	#This is its own method in case more needs to be cleaned