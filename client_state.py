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

on_toxic_message = "Message has been marked for toxicity:\nUser: {}\nChannel: {}\nTime: {}\nMessage: {}\nCertainty: {}"

do_not_reply = "I do not reply to private messages. If you have any questions, please message one of the mods, preferably Oppen_heimer."

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

# This should be within the class
def same_message_response(recent_channel_messages, channel_id):
	if len(recent_channel_messages[channel_id]) > 3:
		recent_channel_messages[channel_id].pop(0)
	if len(recent_channel_messages[channel_id]) < 3:
		return False
	s = recent_channel_messages[channel_id][0].content.lower()
	author_check = recent_channel_messages[channel_id][0].author.id
	if s == recent_channel_messages[channel_id][1].content.lower() and s == recent_channel_messages[channel_id][2].content.lower():
		if author_check != recent_channel_messages[channel_id][1].author.id and author_check != recent_channel_messages[channel_id][2].author.id and recent_channel_messages[channel_id][2] != recent_channel_messages[channel_id][1]:
			return True
	return False


class client_state:
	def __init__(self, client):
		self._client = client
		self._recording = False
		self._message = None
		self._recent_channel_messages = {}
		self._recent_message_repeat_counter = 0
		self._recent_message_repeat_clock = datetime.now() - timedelta(hours=1)
		self._recent_message_cooldown_clock = datetime.now() - timedelta(hours=1)
		self._last_trigger = datetime.now() - timedelta(minutes=10)
		self._last_dadjoke = datetime.now() - timedelta(hours=1)
		self._last_discord_simulation = datetime.now() - timedelta(hours=1)
		for server in self._client.servers:
			for channel in server.channels:
				if server.me.permissions_in(channel).send_messages:
					self._recent_channel_messages[channel.id] = []
		print(self._recent_channel_messages)

	def update_state(self, message):
		self._message = message

	async def get_toxicity(self):
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
			if toxic_score > 91:
				await self._client.send_message(
					self._message.channel,
					"We didn't accept you into this school to be toxic."
					)
				await self._client.delete_message(self._message)
				return True
		return False
	
	async def commands(self):
		# To be refactored even further
		if self._message.content[0:5] == '$send':
			if self._message.author.server_permissions.manage_server:
				if len(self._message.channel_mentions) != 0:
					await self._client.send_message(self._message.channel_mentions[0], prune(self._message.content))
					if self._message.content[5] == 'h':
						await self._client.delete_message(self._message)
				else:
					await self._client.send_message(self._message.channel, 'Syntax is "$send [channel mention] text"')
			else:
				await self._client.send_message(self._message.channel, 'Invalid Permissions')
		elif self._message.content[0:7] == '$record' and self._message.author.server_permissions.manage_server:
			if self._recording is None:
				recordconvo.record_init()
				self._recording = self._message.channel
			else:
				await self._client.send_message(self._message.channel, "Already recording in %s" % (self._recording.mention))
		elif self._message.content == '$trivia':
			await self._client.send_message(self._message.channel, "We do not have enough trivia questions. This feature will be available in the future")
			#await trivia_question(self._client, self._message.channel)
		elif self._message.content[0:11] == '$stoprecord' and self._message.author.server_permissions.manage_server:
			recordconvo.record_end()
			self._recording = None
		elif self._message.content[0:8] == '$catfact':
			await self._client.send_message(self._message.channel, 'Thank you for subscribing to CatFacts™! Did you know:\n `%s`\n\nType "UNSUBSCRIBE" to stop getting cat facts' % get_random_catfact())	

	async def private_message(self):
		if self._message.channel.is_private:
			try:
				await self._client.send_message(self._message.author, content=(do_not_reply))
				print('{}\n{}'.format(self._message.author, self._message.content))
				return True
			except:
				print('Error with private message')

	async def invalid_intro(self):
		if self._message.channel.id == server_id:
			if self._message.content[0] not in '012345':
				try:
					await self._client.send_message(self._message.author, content=(on_invalid_intro))
				except:
					print('Error with invalid_intro')
				await self._client.delete_message(self._message)

	async def recent_messages(self):
		if self._message.channel.id in self._recent_channel_messages.keys():
			self._recent_channel_messages[self._message.channel.id].append(self._message)
			is_same = same_message_response(self._recent_channel_messages, self._message.channel.id)
			if is_same:
				if self._recent_message_repeat_clock <= self._message.timestamp and self._recent_message_cooldown_clock <= self._message.timestamp:
					self._recent_message_repeat_counter = 0
					self._recent_message_repeat_clock = self._message.timestamp + timedelta(hours=1)
				if self._recent_message_repeat_counter >= 3: #placeholder value
					self._recent_message_cooldown_clock = self._message.timestamp + timedelta(hours=1)
					await self._client.send_message(self._message.channel, 'Please stop trying to abuse me')
				else:
					await self._client.send_message(self._message.channel, self._message.content)
					self._recent_message_repeat_counter += 1
				self._recent_channel_messages[self._message.channel.id].clear()


	async def unsubscribe(self):
		if self._message.content[:11].lower() == "unsubscribe":
			await self._client.send_message(self._message.channel, 'Thank you for subscribing to CatFacts™! Did you know:\n `%s`\n\nType "UNSUBSCRIBE" to stop getting cat facts' % get_random_catfact())

	async def trigger(self):
		if self._message.timestamp - self._last_trigger > timedelta(minutes=10):
			for option, words in trigger_words.items():
				if option not in gauchito_only:
					if contains(self._message.content, words):
						self._last_trigger = self._message.timestamp
						await self._client.send_message(self._message.channel, choiced_responses[option])
						break
				elif gauchito_id in [role.id for role in self._message.author.roles]:
					if contains(self._message.content, words):
						self._last_trigger = self._message.timestamp
						await self._client.send_message(self._message.channel, choiced_responses[option])
						break

	async def imdadjoke(self):
		if self._message.timestamp - self._last_dadjoke > timedelta(hours=1):
			joke_content = self._message.content.split()
			for i, word in enumerate(joke_content):
				if word.lower() == 'im' or word.lower() == 'i\'m':
					if len(joke_content[i:]) < 3 and len(joke_content[i:]) > 1:
						joke_content[i] = 'Hi'
						message_to_send = ' '.join(joke_content[i:]) + ", I'm Chancellor Yang"
						self._last_dadjoke = self._message.timestamp
						await self._client.send_message(self._message.channel, message_to_send)
						return

	async def discord_simulation(self):
		if len(self._message.content.split()) > 2 and self._message.channel.id not in no_simulate:
			with open(message_cache_ucsb, 'a') as file:
				file.write(self._message.clean_content + '\n')
		if self._message.timestamp - self._last_discord_simulation >= SIMULATION_INTERVAL:
			simulated_message = simulate(message_cache_ucsb)
			if simulated_message is not None:
				await self._client.send_message(self._message.server.get_channel(sim_channel_id), simulated_message)
				open(message_cache_ucsb, 'w').close()

				self._last_discord_simulation = self._message.timestamp

	async def run(self):
		private = await self.private_message()
		if not private:
			if (await self.get_toxicity()):
				return
			await self.commands()
			await self.invalid_intro()
			await self.recent_messages()
			await self.unsubscribe()
			await self.trigger()
			await self.imdadjoke()
			await self.discord_simulation()
