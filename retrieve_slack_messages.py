import requests
import json
import argparse
import datetime
import os

section_assignments = {'UF42BG2AZ': 'A', 'UF7J9GDF0': 'A', 'UF1DQSB5X': 'A', 'UF1H5UPQS': 'A',
 'UF7F8NZBQ': 'A', 'UF4CHR0C8': 'A', 'UF43ER6VC': 'A', 'UF41X1ECV': 'A',
 'UF2V78H7H': 'A', 'UF209NTPC': 'A', 'UF6E8F22J': 'A', 'UF3CMBX46': 'A',
 'UF2G6AX08': 'A', 'UF138ES92': 'A', 'UF6FTCAPR': 'A', 'UF19DNZ5E': 'A',
 'UF6R87N5A': 'B', 'UF454AYP8': 'B', 'UF6EDFNBF': 'B', 'UF4GQD2BC': 'B',
 'UF4U21CTY': 'B', 'UF16E8535': 'B', 'UF3CE2LBC': 'B', 'UF0Q9EE7K': 'B',
 'UF1FCTP0A': 'B', 'UF267S3U1': 'B', 'UF1365RQU': 'B', 'UF6B2RSL8': 'B',
 'UF7DBQNF6': 'B', 'UF8FVA206': 'B', 'UF6UNDAHY': 'B', 'UF7MR1NEA': 'B'}

def slack_query(query_name, url_data = {}):
	url = 'https://slack.com/api/'
	request_url = '{0}{1}?'.format(url, query_name)
	api_token=os.environ['SLACKKEY']
	url_data['token'] = api_token
	response = requests.get(request_url, params = url_data)
	data = json.loads(response.text)
	return data

def get_channel_list(channels_to_exclude = []):
	channels = {}
	data = slack_query('conversations.list')
	for channel in data['channels']:
		if channel['name'] not in channels_to_exclude:
			channels[channel['name']] = {'id': channel['id']}
	return channels

def get_users(users_to_exclude = []):
	users = {}
	data = slack_query('users.list')
	for user in data['members']:
		if user['id'] not in users_to_exclude:
			users[user['id']] = {'name': user['real_name'], 'section':section_assignments[user['id']]}
	return users

def get_channel_history(channel_id, channel_name, user_list):
	data = slack_query('conversations.history', url_data={'channel':channel_id, 'count':1000})
	posts_to_exclude = ['channel_topic', 'channel_join', 'pinned_item', 'bot_message', 'channel_purpose', 'channel_archive', 'channel_name']
	if 'messages' in data:
		filtered_data = [message for message in data['messages'] if 'subtype' not in message.keys() or message['subtype'] not in posts_to_exclude]
		messages = []
		for message in filtered_data:
			if 'subtype' not in message.keys() or message['subtype'] != 'file_comment':
				user_id = message['user']
				timestamp = message['ts']
				text = message['text']
			else:
				user_id = message['comment']['user']
				timestamp = message['comment']['timestamp']
				text = message['comment']['comment']

			if user_id in user_list:
				timestamp = datetime.datetime.fromtimestamp(float(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
				messages.append({'channel':channel_name, 'user':user_list[user_id]['name'], 'ts':timestamp, 'text':text})
				messages[-1]['section'] = user_list[message['user']]['section']
				messages[-1]['post'] = 1
				messages[-1]['words'] = len(messages[-1]['text'].split(' '))
				messages[-1]['characters'] = len(messages[-1]['text'])
	else:
		messages = []
	return messages

def get_all_messages():
	channels_to_exclude = ['scratchwork']
	channels = get_channel_list(channels_to_exclude)

	users_to_exclude = ['USLACKBOT', 'UEVMEUTU0', 'UEWCD304A', 'UF7RLN6TS', 'UFA88MRP1']
	user_list = get_users(users_to_exclude)

	messages = []
	for channel in channels:
		print('Retrieving #{0} history...'.format(channel))
		messages += get_channel_history(channels[channel]['id'], channel, user_list)
	return messages

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-f', '--file', help = 'output_file')

	data = get_all_messages()

	args = parser.parse_args()
	if args.file:
		with open(args.file + '.json', 'w') as outfile:
			json.dump(data, outfile)
