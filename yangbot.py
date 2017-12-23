import discord
import asyncio
import secretvalues
from datetime import datetime
from datetime import timedelta
def prune(send_message):
	pos = send_message.find('>')
	return send_message[pos+1:]


def contains(text, choices):
	split_text = text.split()
	split_text = [s.lower() for s in split_text]
	for word in choices:
		if word in split_text:
			return True
	return False


server_id, gauchito_id, login_token = secretvalues.get_values()

on_join_message = "Hello, %s, and welcome to the UCSB Discord Server!\n \nWe ask that you introduce yourself so that the other members can get to know you better. Please post an introduction to our dedicated introductions channel with the following format:\n\n1) Discord handle (username#XXXX)\n2) School/Year/Major or the equivalent (UCSB/3rd/Underwater Basketweaving)\n3) Reason for joining the server (Make new friends)\n4) How you found us. If you found us through another person, please list their name or their discord handle because we like to keep track of who invites other people.\n \nAlso, please read the rules. We don't want to have to ban you because you failed to read a short list of rules.\n \n \n(Disclaimer: This bot is NOT Chancellor Yang, and does not represent his opinions. Attributing anything said by this bot to Chancellor Yang will result in a swift banning)" 


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

client = discord.Client()


async def trigger(message):
	global last_trigger
	for option, words in trigger_words.items():
		if option not in gauchito_only:
			if contains(message.content, words):
				last_trigger = datetime.now()
				await client.send_message(message.channel, choiced_responses[option])
				break
		elif gauchito_id in [role.id for role in message.author.roles]:
			if contains(message.content, words):
				last_trigger = datetime.now()
				await client.send_message(message.channel, choiced_responses[option])
				break

async def yang_send(message):
	if message.author.server_permissions.manage_server:
		if len(message.channel_mentions) != 0:
			await client.send_message(message.channel_mentions[0], prune(message.content))
			if message.content[5] == 'h':
				await client.delete_message(message)
		else:
			await client.send_message(message.channel, 'Syntax is "$send [channel mention] text"')
	else:
		await client.send_message(message.channel, 'Invalid Permissions')


@client.event
async def on_ready():
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('--------')

@client.event
async def on_message(message):
	#TODO stuff
	global last_trigger
	try:
		if message.server.id == server_id and message.author != client.user:
			if message.content[0:5] == '$send':
				await yang_send(message)
			elif message.timestamp - last_trigger > timedelta(minutes=2):
				await trigger(message)
	except:
		print('There was an error somewhere in on_message')


@client.event
async def on_member_join(member):
	try:
		await client.send_message(member, content=(on_join_message % (member.mention)))
	except:
		print('There was an error somewhere in on_member_join')

last_trigger = datetime.now() - timedelta(minutes=2)
client.run(login_token)
