import requests
import json
import argparse
import os

team_boards = ['5c377c57d55dc2316170ba48', '5c37638faea70f1ce1fe97ef', '5c377c5745d2916e572cb4e7', '5c377c5ac950f37ab1f855a6', '5c37811c19d071436041d2ed',
'5c362a4c05e14d4511f677a5', '5c33d6c4d559f019e14cf451', '5c361a3e02ecb684511a4dad', '5c362a4da2945e78b830728d', '5c362aee39b3cb8bae066f92', '5c36142c81f94882f08a921a',
'5c362a469ccde91a98d37b22', '5c36132d054082518e2a33ae','5c37635e2df5d87f625aad97', '5c376384382b4c7b8b3977a9', '5c37630d47cf330c9466cda9']

key = os.environ['TRELLOKEY']
token = os.environ['TRELLOTOKEN']

base_url = "https://api.trello.com/1/boards/"
url_params = {'key':key, 'token':token}

def get_action_data():
	data = {}
	for board in team_boards:
		board_response = requests.get(base_url + board, params = url_params)
		board_response_data = json.loads(board_response.text)

		board_data = {}
		board_data['name'] = board_response_data['name']
		print('Retrieving data from ' + board_data['name'] + '...')

		board_data['actions'] = []
		board_data['members'] = set()

		url_params['limit'] = 1000
		actions_response = requests.get(base_url + board + '/actions', params = url_params)
		actions_response_data = json.loads(actions_response.text)

		for action in actions_response_data:
			member = action['memberCreator']['fullName']
			board_data['members'].add(member)
			if 'list' in action['data'].keys() and 'name' in action['data']['list'].keys():
				action_name = action['data']['list']['name']
			elif 'card' in action['data'].keys():
				action_name = action['data']['card']['name']
			else:
				action_name = None
			board_data['actions'].append({'member':member, 'type':action['type'], 'action_name':action_name, 'time':action['date'][:10]})

		print(len(board_data['actions']))
		board_data['members'] = list(board_data['members'])
		data[board] = board_data
	return data


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-f', '--file', help = 'output_file')

	data = get_action_data()

	args = parser.parse_args()
	if args.file:
		with open(args.file + '.json', 'w') as outfile:
			json.dump(data, outfile)