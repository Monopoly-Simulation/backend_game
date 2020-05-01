#!/usr/bin/python
import util
from game import Game
from util import log, metadata, dev_print, prod_print, is_prod
# from results import *
from objects import Player
import random
import time
import argparse
import numpy as np
import json
import matplotlib.pyplot as plt

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
	# dev_print(args.__dict__)
	n_t_s = len(args.trading_strategy)
	n_u_s = len(args.upgrading_strategy)
	n_b_s = len(args.buying_strategy)
	n_t_r = len(args.trading_range)
	n_u_r = len(args.upgrading_range)
	n_b_r = len(args.buying_range)
	n_income = len(args.income)
	n_tax = len(args.tax)
	n_b_tax = len(args.building_tax)
	n_start_capital = len(args.start_capital)
	n_dic = {"trading_strategy": n_t_s,
			"upgrading_strategy": n_u_s,
			"buying_strategy": n_b_s,
			"trading_range": n_t_r,
			"upgrading_range": n_u_r,
			"buying_range": n_b_r,
			"income": n_income,
			"tax": n_tax,
			"start_capital": n_start_capital,
			"building_tax": n_b_tax}
	if args.mode == 0:
		change_variable = None
		count = 0
		for key, value in n_dic.items():
			if value != 1:
				count += 1
				change_variable = key
		if count != 1:
			return False, None
		number = args.__dict__[change_variable][2]
		for key in n_dic.keys():
			if key != change_variable:
				if "strategy" in key:
					args.__dict__[key] *= n_players
				else:
					args.__dict__[key] = [args.__dict__[key][0], 0, number] * n_players
			else:
				args.__dict__[key] *= n_players
		args.change_variable = change_variable
		return True, args
	elif args.mode == 1 or args.mode == 3:

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
			args.income *= n_players
		if n_tax == 3:
			args.tax *= n_players
		if n_b_tax == 3:
			args.building_tax *= n_players
		if n_start_capital == 3:
			args.start_capital *= n_players
		n_t_s = len(args.trading_strategy)
		n_u_s = len(args.upgrading_strategy)
		n_b_s = len(args.buying_strategy)
		n_t_r = len(args.trading_range)
		n_u_r = len(args.upgrading_range)
		n_b_r = len(args.buying_range)
		n_income = len(args.income)
		n_tax = len(args.tax)
		n_b_tax = len(args.building_tax)
		n_start_capital = len(args.start_capital)

		v1 = (n_players == n_t_s == n_u_s == n_b_s) and (
					n_b_tax == n_income == n_tax == n_start_capital == n_t_r == n_u_r == n_b_r == n_players * 3)
		if args.mode == 1:
			v = v1
		else:
			v = v1 and check_same_n_of_paras(n_players, args.trading_range) and check_same_n_of_paras(n_players,
																									  args.upgrading_range) and \
				check_same_n_of_paras(n_players, args.buying_range) and check_same_n_of_paras(n_players, args.income) and \
				check_same_n_of_paras(n_players, args.tax) and check_same_n_of_paras(n_players, args.start_capital) and check_same_n_of_paras(n_players, args.building_tax)
		return v, args

	elif args.mode == 2:
		for u, v in n_dic.items():
			if v == 1:
				pass
			elif v == 3:
				tmp = args.__dict__[u]
				args.__dict__[u] = [tmp[0] + k * tmp[1] for k in range(int(tmp[2]))]
			else:
				return False, None

		return True, args
	else:
		raise ValueError("Unknown mode.")


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
	dev_print("Starting simulation")

	# Set simulation variables
	num_of_players = args.players
	# Go through set amount of simulations
	# Start a new game, run it and save the results
	# dev_print(args.trading_range)
	# dev_print(args.upgrading_range)
	b_strategy = args.buying_strategy
	u_strategy = args.upgrading_strategy
	t_strategy = args.trading_strategy
	# for k in range(num_of_players):
	# 	dev_print(np.arange(args.buying_range[k * 3], args.buying_range[k * 3 + 1], args.buying_range[k * 3 + 2]))
	# single_player_param_list = []
	# for params in player_params:
	#
	# 	single_player_param_list.append(generate_combination(num=7, params=params))
	# # dev_print(single_player_param_list)
	# single_player_list = []
	player_combination = None
	if args.mode in [0, 1, 3]:
		b_range = [
			[args.buying_range[k * 3] + args.buying_range[k * 3 + 1] * i for i in range(int(args.buying_range[k * 3 + 2]))] for k
			in
			range(num_of_players)]
		u_range = [[args.upgrading_range[k * 3] + args.upgrading_range[k * 3 + 1] * i for i in
					range(int(args.upgrading_range[k * 3 + 2]))] for k in range(num_of_players)]
		t_range = [[args.trading_range[k * 3] + args.trading_range[k * 3 + 1] * i for i in range(int(args.trading_range[k * 3 + 2]))]
				   for k in
				   range(num_of_players)]
		income = [[args.income[k * 3] + args.income[k * 3 + 1] * i for i in range(int(args.income[k * 3 + 2]))] for k in range(num_of_players)]
		tax = [[args.tax[k * 3] + args.tax[k * 3 + 1] * i for i in range(int(args.tax[k * 3 + 2]))] for k in range(num_of_players)]
		b_tax = [[args.building_tax[k * 3] + args.building_tax[k * 3 + 1] * i for i in range(int(args.building_tax[k * 3 + 2]))] for k in
				 range(num_of_players)]
		start_capital = [
			[args.start_capital[k * 3] + args.start_capital[k * 3 + 1] * i for i in range(int(args.start_capital[k * 3 + 2]))]
			for k in
			range(num_of_players)]

		player_params = [[b_range[k], u_range[k], t_range[k], income[k], tax[k], start_capital[k], b_tax[k]] for k in
						 range(num_of_players)]
		# dev_print(player_params)
		if args.mode == 3:
			single_player_param_list = []
			for params in player_params:
				single_player_param_list.append(generate_combination(num=7, params=params))
			# dev_print(single_player_param_list)
			single_player_list = []
			for num in range(num_of_players):
				tmp = []
				for p in single_player_param_list[num]:
					tmp.append(Player(num=num, buying_strategy=b_strategy[num], upgrading_strategy=u_strategy[num],
									trading_strategy=t_strategy[num],
									buying_para=p[0], upgrading_para=p[1], trading_para=p[2], income=p[3], tax=p[4],
									start_capital=p[5], building_tax=p[6]))
				single_player_list.append(tmp)

			player_combination = generate_combination(num=num_of_players, params=single_player_list)
		elif args.mode == 0 or args.mode == 1:
			n = int(args.tax[2])
			player_combination = []
			for i in range(n):
				tmp = []
				for num in range(num_of_players):
					tmp_player = Player(num=num, buying_strategy=b_strategy[num], upgrading_strategy=u_strategy[num],
										trading_strategy=b_strategy[num],
										buying_para=b_range[num][i], upgrading_para=u_range[num][i],
										trading_para=t_range[num][i],
										income=income[num][i], tax=tax[num][i], start_capital=start_capital[num][i], building_tax=b_tax[num][i])

					tmp.append(tmp_player)
				player_combination.append(tmp)
	elif args.mode == 2:
		player_combination = []
		para_list = [args.buying_range, args.upgrading_range, args.trading_range, args.income, args.tax, args.start_capital, args.building_tax]
		para_combination = generate_combination(7, para_list)
		for p in para_combination:
			tmp = []
			for i in range(num_of_players):
				tmp.append(Player(num=i, buying_strategy=args.buying_strategy[0], upgrading_strategy=args.upgrading_strategy[0],
												trading_strategy=args.trading_strategy[0], buying_para=p[0], upgrading_para=p[1], trading_para=p[2],
												income=p[3], tax=p[4], start_capital=p[5], building_tax=p[6]))
			player_combination.append(tmp)
	else:
		raise ValueError("Unknown type.")

	count = 1
	last = time.time()
	simulation_list = []
	for players in player_combination:
		cur_simulation_dic = {"settings": {}, "details": {}, "results": {}}
		player_info_lst = []
		for i in range(len(players)):
			cur_player_dic = {
				"buy_s": players[i].b_strategy,
				"buy_para": players[i].b_para,
				"trade_s": players[i].t_strategy,
				"trade_para": players[i].t_para,
				"upgrade_s": players[i].u_strategy,
				"upgrade_para": players[i].u_para,
				"income": players[i].income,
				"tax": players[i].tax,
				"start_capital": players[i].start_capital,
				"building_tax": players[i].building_tax}
			player_info_lst.append(cur_player_dic)
		cur_simulation_dic["settings"] = player_info_lst

		total_rounds = 0
		valid_simulation = 0
		if util.verbose:
			log.write("player combination: " + str(players) + "\n")
		for i in range(1, args.number + 1):
			if util.verbose:
				log.write("simulation number" + str(i) + "\n")
			for n in players:
				n.reset()
			g = Game(players, rounds=args.rounds)
			tmp_info_dic = g.run()

			if tmp_info_dic["end"] != -1:
				total_rounds += tmp_info_dic["end"]
				valid_simulation += 1

			cur_simulation_dic["details"][i] = tmp_info_dic
			if i % 100 == 0:
				dev_print("{} out of {} simulation of combination {} finished.".format(i, args.number, count))

		# r.addHitResults(g.board.hits)

		# Calculate the amount of simulations per second
		now = time.time()
		duration = now - last
		avg_time = duration / args.number
		try:
			avg_round = total_rounds / valid_simulation
		except ZeroDivisionError:
			avg_round = float("inf")
		last = time.time()

		cur_simulation_dic["results"]["avg_time"] = avg_time
		cur_simulation_dic["results"]["avg_round"] = avg_round
		cur_simulation_dic["results"]["total_time"] = duration
		cur_simulation_dic["results"]["end_percent"] = valid_simulation / args.number
		# speed = i / (now - start)
		dev_print("ended: ", valid_simulation)
		dev_print("avg_time: ", avg_time)
		dev_print("avg_round: ", avg_round)
		# Display the progress every 1/1000 of the way to begin finished
		dev_print("{} out of {} combination finished.".format(count, len(player_combination)))
		count += 1
		simulation_list.append(cur_simulation_dic)
	metadata_dic["simulations"] = simulation_list
	prod_print(json.dumps(metadata_dic) + "\n")
	# Print that the simulation is finished
	dev_print("\nDone!")


def get_plot(args):
	if args.__dict__["change_variable"] is not None:
		para_to_plot = args.__dict__[args.__dict__["change_variable"]]
		simulations = metadata_dic["simulations"]
		x = [para_to_plot[0] + para_to_plot[1] * i for i in range(int(para_to_plot[2]))]
		y_round = []
		y_time = []
		y_end_percent = []
		for simulation in simulations:
			y_time.append(simulation["results"]["avg_time"])
			y_round.append(simulation["results"]["avg_round"])
			y_end_percent.append(simulation["results"]["end_percent"])
		plt.subplot(311)
		plt.plot(x, y_time)
		plt.ylabel("avg_time")
		plt.subplot(312)
		plt.plot(x, y_round)
		plt.ylabel("avg_round")
		plt.subplot(313)
		plt.plot(x, y_end_percent)
		plt.ylabel("end_percent")
		plt.show()
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
	parser.add_argument("-b_tax", "--building_tax", type=float, nargs="+", default=[0, 0, 1],
						help="the tax charged on land property, can only be a percentage, [start, step, number]")

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

	parser.add_argument("-mode", "--mode", type=int, default=0, choices=[0, 1, 2, 3],
						help="mode 0: only one variable is changing\nmode 1: linear compare\nmode 2: cross compare uniform players.\nmode 3: cross compare different players")

	parser.add_argument("-plot", "--change_variable", default=None)
	args = parser.parse_args()

	valid, args = check_validity_and_broadcast(args)
	if valid:
		# Run simulation
		run_simulation(args)
	else:
		raise ValueError("parameter input not valid, please use -h option for help.")
	if not is_prod:
		get_plot(args)
