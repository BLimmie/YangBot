#TODO Delete unused imports
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
import client_state

on_join_message = "Hello, %s, and welcome to the UCSB Discord Server!\n \nWe ask that you introduce yourself so that the other members can get to know you better. Please post an introduction to our dedicated introductions channel with the following format:\n\n1) Discord handle (username#XXXX)\n2) School/Year/Major or the equivalent (UCSB/3rd/Underwater Basketweaving)\n3) Reason for joining the server (Make new friends)\n4) How you found us.\n5) [Optional] Anything you'd like to say\nIf you found us through another person, please list their name or their discord handle because we like to keep track of who invites other people.\n \nAlso, please read the rules. We don't want to have to ban you because you failed to read a short list of rules.\n \n \n(Disclaimer: This bot is NOT Chancellor Yang, and does not represent his opinions.)" 

client = discord.Client()
actions = None
@client.event
async def on_ready():
	global actions
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('--------')
	actions = client_state.client_state(client)
	print('Client State setup complete')

@client.event
async def on_message(message):
	#TODO stuff
	if message.content is not None and message.content != '' and not message.author.bot:
		try:
			actions.update_state(message)
			await actions.run()
		except Exception as e:
			print('There was an error somewhere in on_message: ' +str(e))
			traceback.print_exc()
			print('Message Channel: ' + message.channel.name)
			print('Message Content: ' + message.content)
			print('Message Author: ' + message.author.name + '\n')


@client.event
async def on_message_edit(before, after):
	try:
		if after.server.id == server_id and after.author != client.user:
			if actions._recording is not None and actions._recording == after.channel:
				recordconvo.record_message_edit(after)
	except:
		print('There was an error somewhere in on_message_edit')
		traceback.print_exc()

@client.event
async def on_message_delete(message):
	try:
		if message.server.id == server_id and message.author != client.user:
			if actions._recording is not None and actions._recording == message.channel:
				recordconvo.record_message_delete(message)
	except:
		print('There was an error somewhere in on_message_delete')
		traceback.print_exc()


@client.event
async def on_reaction_add(reaction, user):
	try:
		if not reaction.me:
			await client.add_reaction(reaction.message, reaction.emoji)
	except:
		print('There was an error somewhere in on_reaction_add')
		traceback.print_exc()


@client.event
async def on_reaction_remove(reaction, user):
	try:
		if reaction.count == 1 and reaction.me:
			await client.remove_reaction(reaction.message, reaction.emoji, reaction.message.server.me)
	except Exception as e:
		print('There was an error somewhere in on_reaction_remove: ' + str(e))
		traceback.print_exc()

@client.event
async def on_member_join(member):
	try:
		await client.send_message(member, content=(on_join_message % (member.mention)))
	except:
		print('There was an error somewhere in on_member_join')
		traceback.print_exc()

@client.event
async def on_member_update(before,after):
	try:
		if after.id == '285607618913894402': #user id here
			role_whitelist = ['322140419448242176','338236189738008576','338230169875775499'] #admin, regular, friendo
			undesired_roles = []
			for role in after.roles:
				if role.id not in role_whitelist:
					undesired_roles.append(role)
			await client.remove_roles(after, *undesired_roles)
	except:
		print('There was an error somewhere in on_member_update')
		traceback.print_exc()


client.run(login_token)
