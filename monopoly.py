#!/usr/bin/python
import util
from game import Game
from util import log, metadata
# from results import *
from objects import Player
import random
import time
import argparse
import numpy as np
import json


random.seed(0)
metadata_dic = {}


def check_same_n_of_paras(n, lst):
	base = lst[2]
	for i in range(n):
		if lst[i * 3 + 2] != base:
			return False
	return True


def check_validity_and_broadcast(args):
	n_players = args.players
	n_t_s = len(args.trading_strategy)
	n_u_s = len(args.upgrading_strategy)
	n_b_s = len(args.buying_strategy)
	n_t_r = len(args.trading_range)
	n_u_r = len(args.upgrading_range)
	n_b_r = len(args.buying_range)
	n_income = len(args.income)
	n_tax = len(args.tax)
	n_start_capital = len(args.start_capital)
	if n_t_s == 1:
		args.trading_strategy *= n_players
	if n_b_s == 1:
		args.buying_strategy *= n_players
	if n_u_s == 1:
		args.upgrading_strategy *= n_players
	if n_t_r == 3:
		args.trading_range *= n_players
	if n_u_r == 3:
		args.upgrading_range *= n_players
	if n_b_r == 3:
		args.buying_range *= n_players
	if n_income == 3:
		args.income *= 3
	if n_tax == 3:
		args.tax *= 3
	if n_start_capital == 3:
		args.start_capital *= 3
	n_t_s = len(args.trading_strategy)
	n_u_s = len(args.upgrading_strategy)
	n_b_s = len(args.buying_strategy)
	n_t_r = len(args.trading_range)
	n_u_r = len(args.upgrading_range)
	n_b_r = len(args.buying_range)
	n_income = len(args.income)
	n_tax = len(args.tax)
	n_start_capital = len(args.start_capital)

	v1 = (n_players == n_t_s == n_u_s == n_b_s) and (n_income == n_tax == n_start_capital == n_t_r == n_u_r == n_b_r == n_players * 3)
	if args.cross_compare:
		v = v1
	else:
		v = v1 and check_same_n_of_paras(n_players, args.trading_range) and check_same_n_of_paras(n_players, args.upgrading_range) and \
			check_same_n_of_paras(n_players, args.buying_range) and check_same_n_of_paras(n_players, args.income) and \
			check_same_n_of_paras(n_players, args.tax) and check_same_n_of_paras(n_players, args.start_capital)
	return v, args


def generate_combination(num, params):
	result = []

	def for_recursive(number_of_loops, range_list, current_index=0, iter_list=[]):
		if iter_list == []:
			iter_list = [0] * number_of_loops

		if current_index == number_of_loops - 1:
			for iter_list[current_index] in range_list[current_index]:
				result.append(iter_list[:])
		else:
			for iter_list[current_index] in range_list[current_index]:
				for_recursive(number_of_loops, iter_list=iter_list, range_list=range_list,
							  current_index=current_index + 1)

	for_recursive(num, range_list=params)
	return result


def run_simulation(args):
	# Init results class for saving the results
	# r = Results()
	if args.verbose:
		util.verbose = True
	# Print start message
	print("Starting simulation")

	# Set simluation variables
	num_of_players = args.players
	# Go through set amount of simulations
	# Start a new game, run it and save the results
	# print(args.trading_range)
	# print(args.upgrading_range)
	b_strategy = args.buying_strategy
	u_strategy = args.upgrading_strategy
	t_strategy = args.trading_strategy
	# for k in range(num_of_players):
	# 	print(np.arange(args.buying_range[k * 3], args.buying_range[k * 3 + 1], args.buying_range[k * 3 + 2]))

	b_range = [[args.buying_range[k * 3] + args.buying_range[k * 3 + 1] * i for i in range(args.buying_range[k * 3 + 2])] for k in
			   range(num_of_players)]
	u_range = [[args.upgrading_range[k * 3] + args.upgrading_range[k * 3 + 1] * i for i in range(args.upgrading_range[k * 3 + 2])] for k in
			   range(num_of_players)]
	t_range = [[args.trading_range[k * 3] + args.trading_range[k * 3 + 1] * i for i in range(args.trading_range[k * 3 + 2])] for k in
			   range(num_of_players)]
	income = [[args.income[k * 3] + args.income[k * 3 + 1] * i for i in range(args.income[k * 3 + 2])] for k in
			   range(num_of_players)]
	tax = [[args.tax[k * 3] + args.tax[k * 3 + 1] * i for i in range(args.tax[k * 3 + 2])] for k in
			   range(num_of_players)]
	start_capital = [[args.start_capital[k * 3] + args.start_capital[k * 3 + 1] * i for i in range(args.start_capital[k * 3 + 2])] for k in
			   range(num_of_players)]

	player_params = [[b_range[k], u_range[k], t_range[k], income[k], tax[k], start_capital[k]] for k in
					 range(num_of_players)]
	# print(player_params)
	single_player_param_list = []
	for params in player_params:
		single_player_param_list.append(generate_combination(num=6, params=params))
	# print(single_player_param_list)
	single_player_list = []
	if args.cross_compare:
		for num in range(num_of_players):
			tmp = []
			for p in single_player_param_list[num]:
				tmp.append(Player(num=num, buying_strategy=b_strategy[num], upgrading_strategy=u_strategy[num],
								  trading_strategy=t_strategy[num],
								  buying_para=p[0], upgrading_para=p[1], trading_para=p[2]))
			single_player_list.append(tmp)

		player_combination = generate_combination(num=num_of_players, params=single_player_list)
	else:
		n = args.tax[2]
		player_combination = []
		for i in range(n):
			tmp = []
			for num in range(num_of_players):
				tmp.append(Player(num=num, buying_strategy=b_strategy[num], upgrading_strategy=u_strategy[num], trading_strategy=b_strategy[num],
								  buying_para=b_range[num][i], upgrading_para=u_range[num][i], trading_para=t_range[num][i],
								  income=income[num][i], tax=tax[num][i], cash=start_capital[num][i]))
			player_combination.append(tmp)
	count = 1
	last = time.time()
	for players in player_combination:
		metadata_dic[str(players)] = {}
		total_rounds = 0
		if util.verbose:
			log.write("player combination: " + str(players) + "\n")
		for i in range(1, args.number + 1):
			if util.verbose:
				log.write("simulation number" + str(i) + "\n")
			for n in players:
				n.reset()
			g = Game(players, rounds=args.rounds)
			tmp_info_dic = g.run()
			total_rounds += tmp_info_dic["end"]
			metadata_dic[str(players)][i] = tmp_info_dic
			if i % 100 == 0:
				print("{} out of {} simulation of combination {} finished.".format(i, args.number, count))

			# r.addHitResults(g.board.hits)

			# Calculate the amount of simulations per second
		now = time.time()
		duration = now - last
		avg_time = duration / args.number
		avg_round = total_rounds / args.number
		last = time.time()
		metadata_dic[str(players)]["avg_time"] = avg_time
		metadata_dic[str(players)]["avg_round"] = avg_round
		metadata_dic[str(players)]["total_time"] = duration
		metadata.write(json.dumps(metadata_dic[str(players)]))
		metadata.write("\n")
			# speed = i / (now - start)
		count += 1
		# Display the progress every 1/1000 of the way to begin finished
		print("{} out of {} combination finished.".format(count, len(player_combination)))

	# Print that the simulation is finished
	print("\nDone!")

	# Same the results to a csv
	# r.writeHTML(args.number, args.players, args.rounds)


if __name__ == "__main__":
	# Handle command line arguments
	parser = argparse.ArgumentParser(description="Program to simulate the game of Monopoly.")
	parser.add_argument("-n", "--number", type=int, default=100,
						help="number of simulations to run")
	parser.add_argument("-p", "--players", type=int, choices=[i for i in range(100)],
						default=3, help="number of players to run the simulation with")
	parser.add_argument("-r", "--rounds", type=int, default=1000,
						help="number of rounds to simulate each game")

	parser.add_argument("-i", "--income", type=int, nargs="+", default=[100, 0, 1],
						help="the money every time a player can get when passing go, [start, step, number]")

	parser.add_argument("-tax", "--tax", type=float, nargs="+", default=[0, 0, 1],
						help="the tax charged when a player passes go, can be a percentage or a actual number, "
							 "[start, step, number]")

	parser.add_argument("-sc", "--start_capital", type=int, nargs="+", default=[200, 0, 1],
						help="the money each player has at the beginning of the game, [start, step, number].")

	parser.add_argument("-b", "--buying_strategy", type=int, nargs="+", default=[0],
						help="the strategy that players use to buy buildings, one for each")
	parser.add_argument("-br", "--buying_range", nargs="+", type=float, default=[0.5, 0, 1],
						help="[start, step, number], three for each player")

	parser.add_argument("-u", "--upgrading_strategy", type=int, nargs="+", default=[0],
						help="the strategy that players use to build buildings, one for each")
	parser.add_argument("-ur", "--upgrading_range", nargs="+", type=float, default=[0.5, 0, 1],
						help="[start, step, number], three for each player")

	parser.add_argument("-t", "--trading_strategy", type=int, nargs="+", default=[0],
						help="the strategy that players use to trade, one for each")
	parser.add_argument("-tr", "--trading_range", nargs="+", type=float, default=[0.5, 0, 1],
						help="[start, step, number], three params for each player")

	parser.add_argument("-v", "--verbose", const=True, action="store_const",
						help="if turned on, generate a full log")

	parser.add_argument("-cross", "--cross_compare", const=True, action="store_const",
						help="if turned on, start cross compare, otherwise uses linear compare.")

	args = parser.parse_args()

	valid, args = check_validity_and_broadcast(args)
	if valid:
		# Run simulation
		run_simulation(args)
	else:
		raise ValueError("parameter input not valid, please use -h option for help.")
