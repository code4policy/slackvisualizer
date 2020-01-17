import requests
import json
import argparse
import datetime
import os
import yaml


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
			users[user['id']] = {'name': user['real_name'], 'section': 'not assigned' }
	return users

def get_channel_history(channel_id, channel_name, user_list, posts_to_exclude=[]):
	data = slack_query('conversations.history', url_data={'channel':channel_id, 'count':1000})
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
				messages[-1]['id'] = user_id
	else:
		messages = []
	return messages

def get_all_messages(channels_to_exclude=[], users_to_exclude=[]):
	channels = get_channel_list(channels_to_exclude)
	user_list = get_users(users_to_exclude)
	print(users_to_exclude)
	print(user_list)


	messages = []
	for channel in channels:
		print('Retrieving #{0} history...'.format(channel))
		messages += get_channel_history(channels[channel]['id'], channel, user_list)
	return messages

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-f', '--file', help = 'output_file')

	with open('slack-config.yaml') as f:
		config = yaml.safe_load(f)

	users_to_exclude = config['users_to_exclude']
	channels_to_exclude = config['channels_to_exclude']
	posts_to_exclude = config['posts_to_exclude']
	data = get_all_messages(channels_to_exclude, users_to_exclude)

	args = parser.parse_args()
	if args.file:
		with open(args.file + '.json', 'w') as outfile:
			json.dump(data, outfile)
