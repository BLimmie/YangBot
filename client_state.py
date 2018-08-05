import discord
import asyncio
import secretvalues
import traceback
import random
from datetime import datetime
from datetime import timedelta
import recordconvo
from secretvalues import *
from trigger import *
from discordsim import simulate, message_cache_ucsb, SIMULATION_INTERVAL
from trivia import trivia_question
from catfacts import get_random_catfact
import perspective

do_not_reply = "I do not reply to private messages. If you have any questions, please self._message one of the mods, preferably Oppen_heimer."

on_invalid_intro = "Your self._message has been deleted for not following the introduction format that we have listed out. Please follow the format given.\n\n1) Discord handle (username#XXXX)\n2) School/Year/Major or the equivalent (UCSB/3rd/Underwater Basketweaving)\n3) Reason for joining the server (Make new friends)\n4) How you found us.\n5) [Optional] Anything you'd like to say"

on_toxic_message = "self._message has been marked for toxicity:\nUser: {}\nChannel: {}\nTime: {}\nMessage: {}\nCertainty: {}"

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

def same_message_response(channel_id):
	if len(recent_channel_messages[channel_id]) > 3:
		recent_channel_messages[channel_id].pop(0)
	if len(recent_channel_messages[channel_id]) < 3:
		return False
	s = recent_channel_messages[channel_id][0].content.lower()
	if s == recent_channel_messages[channel_id][1].content.lower() and s == recent_channel_messages[channel_id][2].content.lower():
		if s.author.id != recent_channel_messages[channel_id][1].author.id and s.author.id != recent_channel_messages[channel_id][2].author.id:
			return True
	return False

class client_state:
	def __init__(self, self._client):
		self._client = self._client
		self._recording = false
		self._message = None
		self._recent_channel_messages = {}
		self._last_trigger = datetime.now() - timedelta(minutes=10)
		self._last_discord_simulation = datetime.now - timedelta(hours=1)

	def update_state(self, self._message):
		self._message = self._message

	def get_toxicity(self):
		toxic, toxic_score = perspective.is_toxic(self._message.clean_content)
		if toxic:
			await self._client.send_message(
				self._message.server.get_channel(admin_alerts), 
				on_toxic_message.format(
					self._message.author.display_name, 
					self._message.channel.mention, 
					(self._message.timestamp - timedelta(hours=7)), 
					self._message.clean_content, 
					toxic_score*100
				)
			)

	def invalid_intro(self):
		if self._message.channel.id == server_id:
			if self._message.content[0] not in '012345':
				try:
					await self._client.send_message(self._message.author, content=(on_invalid_intro))
				except:
					print('Error with invalid_intro')
				await self._client.delete_message(self._message)

	def recent_messages(self):
		if self._message.channel.id in self._recent_channel_messages.keys():
			self._recent_channel_messages[self._message.channel.id].append(self._message)
			is_same = same_message_response(self._message.channel.id)
			if is_same:
				await self._client.send_message(self._message.channel, self._message.content)
				self._recent_channel_messages[self._message.channel.id].clear()

	def unsubscribe(self):
		await self._client.send_message(self._message.channel, 'Thank you for subscribing to CatFacts™! Did you know:\n `%s`\n\nType "UNSUBSCRIBE" to stop getting cat facts' % get_random_catfact())

	def trigger(self):
		if self._message.timestamp - self._last_trigger > timedelta(minutes=10):
			for option, words in trigger_words.items():
				if option not in gauchito_only:
					if contains(self._message.content, words):
						self._last_trigger = datetime.now()
						await self._client.send_message(self._message.channel, choiced_responses[option])
						break
				elif gauchito_id in [role.id for role in self._message.author.roles]:
					if contains(self._message.content, words):
						self._last_trigger = datetime.now()
						await self._client.send_message(self._message.channel, choiced_responses[option])
						break

	def discord_simulation(self):
		if len(self._message.content.split()) > 2 and self._message.channel.id not in no_simulate:
			with open(message_cache_ucsb, 'a') as file:
				file.write(self._message.clean_content + '\n')
		if self._message.timestamp - last_discord_simulation >= SIMULATION_INTERVAL:
			simulated_message = simulate(message_cache_ucsb)
			if simulated_message is not None:
				await self._client.send_message(self._message.server.get_channel(sim_channel_id), simulated_message)
				open(message_cache_ucsb, 'w').close()
				last_discord_simulation = self._message.timestamp