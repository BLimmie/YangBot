import discord
import asyncio
import csv
from datetime import datetime


record = open('recorded_messages.csv', 'a')
recorder = csv.writer(record)
print('opened recorded_messages.csv to append')

edit_record = open('edited_recorded_messages.csv', 'a')
edit_recorder = csv.writer(edit_record)
print('opened edited_recorded_messages.csv to append')

def format_record(time_str, message_id, user_id, user_name, message_content):
	return [time_str, message_id, user_id, user_name, message_content]

def record_init():
	recorder.writerow(format_record(
		datetime.now(), 
		None, 
		None, 
		None, 
		"Recording started"
	))

def record_message(message):
	recorder.writerow(format_record(
		message.timestamp, 
		message.id, 
		message.author.id, 
		message.author.name, 
		message.content
	))

def record_message_edit(message):
	edit_recorder.writerow(format_record(
		message.edited_timestamp,
		message.id,
		message.author.id,
		message.author.name,
		message.content
	))

def record_message_delete(message):
	edit_recorder.writerow(format_record(
		datetime.now(),
		message.id,
		message.author.id,
		message.author.name,
		"DELETED"
	))

def record_end():
	recorder.writerow(format_record(
		datetime.now(), 
		None, 
		None, 
		None, 
		"Recording ended"
	))