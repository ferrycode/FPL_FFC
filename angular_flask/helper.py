import requests
import json
import urllib
import os
from collections import Counter, OrderedDict
import csv
import sys
import math
import operator

team_folder = os.path.join(os.getcwd(),'teams')
all_data_url = 'https://fantasy.premierleague.com/drf/bootstrap-static'
dynamic_url = 'https://fantasy.premierleague.com/drf/bootstrap-dynamic'
flatten = lambda l: [item for sublist in l for item in sublist]
order_dict = lambda d: OrderedDict(sorted(d.items(), key = lambda x: x[1], reverse=True))

def get_current_gw():
	response = requests.get(dynamic_url)
	data = response.json()
	return data['current-event']    

def read_in_team(filename):
	player_no = 1
	player_code_table = {}
	target = open(filename, 'r')
	for line in target:
		if ',' not in line:
			team_name = line.strip()
			continue
		else:
			line = line.split(',')
			player_name = line[0]
			player_url = line[1].strip()
			player_id = [int(num) for num in line[1].split('/') if num.isdigit()][0]
			player_code_table[player_no] = (player_name, player_id, player_url)
			player_no+=1
	target.close()
	return team_name, player_code_table

def print_team(player_code_table):
	for player, pid in player_code_table.items():
		print('{} : {}'.format(player, pid[0]))

def soupify(url):
	htmltext = requests.get(url)
	data = htmltext.json()
	return data

pdata = soupify(all_data_url)

player_dir = {}
for player in pdata['elements']:
	player_dir[player['id']] = player['web_name'] #, get_team(player['team']))

team_dir = {}
for team in pdata['teams']:
	team_dir[team['id']] = team['short_name']

def get_team(team_id):
	return team_dir[team_id]

def get_current_team(code, include_captain_twice = False):
	gw = get_current_gw()
	entry_url = "https://fantasy.premierleague.com/drf/entry/%d/event/%d" % (code, gw)
	data = soupify(entry_url)
	current_team, bench = [], []
	for pick in data['picks']:
		if not pick['is_sub']:
			current_team.append(player_dir[pick['element']])
		else: bench.append(player_dir[pick['element']])
		if pick['is_captain'] and include_captain_twice:
			current_team.append(player_dir[pick['element']])
	return current_team, bench

def get_ffcteamdetails(team_file, captain = -1, bench = -1, include_captain_twice = False, include_bench=False):
	team_details = []
	team_file = os.path.join(team_folder,team_file)
	team_name, ffc_team = read_in_team(team_file)
	fpl_codes = [entry[1] for entry in list(ffc_team.values())]
	if bench != -1 and captain != -1:
		fpl_codes[bench-1] = fpl_codes[captain-1]
	elif captain != -1: fpl_codes.append(fpl_codes[captain-1])
	for code in fpl_codes:
		current, bench = get_current_team(code, include_captain_twice)
		team_details.append(current)
		if include_bench:
			team_details.append(bench)
	team_details = flatten(team_details)
	total_count = dict(Counter(team_details))
	total_count_sorted = order_dict(total_count)
	return total_count_sorted

def get_differentials(t1,t2):
	players_both_sides = set(list(t1.keys()) + list(t2.keys()))
	diff = {key: t1.get(key, 0) - t2.get(key, 0) for key in players_both_sides}
	diff_sorted = order_dict(diff)
	return diff_sorted

def team_scoreboard(filename):
	gw = get_current_gw()
	team_file = os.path.join(team_folder,filename)
	team_name, ffc_team = read_in_team(team_file)
	fpl_codes = [entry[1] for entry in list(ffc_team.values())]
	scores = []
	points, transfer_costs = [], []
	player_urls = []
	for code in fpl_codes:
		entry_url = "https://fantasy.premierleague.com/drf/entry/%d/event/%d" % (code, gw)
		fpl_url = "https://fantasy.premierleague.com/a/team/%d/event/%d" % (code, gw)
		player_urls.append(fpl_url)
		data = soupify(entry_url)
		points.append(data['points'])
		transfer_costs.append(data['entry_history']['event_transfers_cost'])
		scores.append(data['points'] - data['entry_history']['event_transfers_cost'])
	player_names = [item[0] for item in list(ffc_team.values())]
	table_content = list(map(list, zip(player_names, points, transfer_costs, scores, player_urls)))
	table_content = sorted(table_content, key=lambda x: x[3], reverse=True)
	board = []
	for row in table_content:
		item = {
			'Player': row[0],
			'Points': row[1],
			'TC': row[2],
			'Score': row[3],
			'Link': row[4]
		}
		board.append(item)
	return board

def get_scores(filename, captain, bench = -1, home_advtg = False):
	total = 0
	scores = []
	gw = get_current_gw()
	team_file = os.path.join(team_folder,filename)
	team_name, ffc_team = read_in_team(team_file)
	fpl_codes = [entry[1] for entry in list(ffc_team.values())]
	if bench != -1:
		fpl_codes[bench-1] = fpl_codes[captain-1]
	else: fpl_codes.append(fpl_codes[captain-1])
	for code in fpl_codes:
		entry_url = "https://fantasy.premierleague.com/drf/entry/%d/event/%d" % (code, gw)
		data = soupify(entry_url)
		scores.append(data['points'] - data['entry_history']['event_transfers_cost'])
	total = sum(scores)
	if home_advtg:
		total += math.ceil(0.25*max(scores))
	return total