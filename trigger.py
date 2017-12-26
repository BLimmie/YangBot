#YangBot's responses
choiced_responses = {
	"dank": "I sure hope you're talking about dank memes and not that dank green!",
	"blaze": "I sure hope you're talking about the pizza!",
	"alcohol": "Reminder that underage drinking is prohibited at UCSB.", #should only be triggered by gauchito
	"mj": "Despite the passing of Prop 64, marijuana usage is prohibited at UCSB except for university-approved research.",
	"adderall": "If you need to study, go to the UCSB Library. Most people focus the best on the 8th floor.",
	"fire": "Put on a mask and get back to studying",
	"drug": "Substance abuse is prohibited at UCSB",
	"party": "Go back to studying"
}


#Words that trigger YangBot. These are directly connected to the responses above with the words on the left
trigger_words = {
	"dank": ['dank'],
	"blaze": ['blaze'],
	"alcohol": ['alcohol', 'vodka', 'wine', 'beer', 'drunk', 'whiskey', 'beers'], #should only be triggered by gauchito
	"mj": ['mj', '420', 'weed', 'kush', 'marijuana'],
	"adderall": ['adderall', 'adderal', 'addy'],
	"drug": ['drug', 'acid', 'lsd', 'shrooms', 'xanax', 'coke', 'cocaine'],
	"fire": ['fire'],
	"party": ['party']
}


#Words that only are triggered by gauchitos
gauchito_only = ["alcohol", "party"]