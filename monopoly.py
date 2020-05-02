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
import multiprocessing as mp


# random.seed(0)
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
	n_s = len(args.strategy)
	if n_s == 1:
		args.strategy *= n_players
	n_s_r = len(args.strategy_parameter)
	n_income = len(args.income)
	n_tax = len(args.tax)
	n_b_tax = len(args.building_tax)
	n_start_capital = len(args.start_capital)
	n_dic = {"strategy_parameter": n_s_r,
			"income": n_income,
			"tax": n_tax,
			"start_capital": n_start_capital,
			"building_tax": n_b_tax}
	if args.mode == 1 or args.mode == 3:

		if n_s_r == 3:
			args.strategy_parameter *= n_players
		if n_income == 3:
			args.income *= n_players
		if n_tax == 3:
			args.tax *= n_players
		if n_b_tax == 3:
			args.building_tax *= n_players
		if n_start_capital == 3:
			args.start_capital *= n_players
		n_s = len(args.strategy)
		n_s_r = len(args.strategy_parameter)
		n_income = len(args.income)
		n_tax = len(args.tax)
		n_b_tax = len(args.building_tax)
		n_start_capital = len(args.start_capital)

		v1 = (n_players == n_s) and (
					n_b_tax == n_income == n_tax == n_start_capital == n_s_r == n_players * 3)
		if args.mode == 1:
			v = v1
		else:
			v = v1 and check_same_n_of_paras(n_players, args.strategy_parameter) and check_same_n_of_paras(n_players, args.income) and \
				check_same_n_of_paras(n_players, args.tax) and check_same_n_of_paras(n_players, args.start_capital) and check_same_n_of_paras(n_players, args.building_tax)
		return v, args

	elif args.mode == 2:
		count = 0
		change_variable = None
		for u, v in n_dic.items():
			if v == 1:
				pass
			elif v == 3:
				count += 1
				tmp = args.__dict__[u]
				args.__dict__[u] = [tmp[0] + k * tmp[1] for k in range(int(tmp[2]))]
				change_variable = u
			else:
				return False, None
		if count == 1:
			args.change_variable = change_variable
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


def generate_player_combination(args):
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
	strategy = args.strategy
	# for k in range(num_of_players):
	# 	dev_print(np.arange(args.buying_range[k * 3], args.buying_range[k * 3 + 1], args.buying_range[k * 3 + 2]))
	# single_player_param_list = []
	# for params in player_params:
	#
	# 	single_player_param_list.append(generate_combination(num=7, params=params))
	# # dev_print(single_player_param_list)
	# single_player_list = []
	player_combination = None
	if args.mode in [1, 3]:
		strategy_parameter = [
			[args.strategy_parameter[k * 3] + args.strategy_parameter[k * 3 + 1] * i for i in range(int(args.strategy_parameter[k * 3 + 2]))] for k
			in
			range(num_of_players)]
		income = [[args.income[k * 3] + args.income[k * 3 + 1] * i for i in range(int(args.income[k * 3 + 2]))] for k in range(num_of_players)]
		tax = [[args.tax[k * 3] + args.tax[k * 3 + 1] * i for i in range(int(args.tax[k * 3 + 2]))] for k in range(num_of_players)]
		b_tax = [[args.building_tax[k * 3] + args.building_tax[k * 3 + 1] * i for i in range(int(args.building_tax[k * 3 + 2]))] for k in
				 range(num_of_players)]
		start_capital = [
			[args.start_capital[k * 3] + args.start_capital[k * 3 + 1] * i for i in range(int(args.start_capital[k * 3 + 2]))]
			for k in
			range(num_of_players)]

		player_params = [[strategy_parameter[k], income[k], tax[k], start_capital[k], b_tax[k]] for k in range(num_of_players)]
		# dev_print(player_params)
		if args.mode == 3:
			single_player_param_list = []
			for params in player_params:
				single_player_param_list.append(generate_combination(num=5, params=params))
			# dev_print(single_player_param_list)
			single_player_list = []
			for num in range(num_of_players):
				tmp = []
				for p in single_player_param_list[num]:
					tmp.append(Player(num=num, strategy=strategy[num], strategy_para=p[0], income=p[1], tax=p[2],
									start_capital=p[3], building_tax=p[4]))
				single_player_list.append(tmp)

			player_combination = generate_combination(num=num_of_players, params=single_player_list)
		elif args.mode == 1:
			n = int(args.tax[2])
			player_combination = []
			for i in range(n):
				tmp = []
				for num in range(num_of_players):
					tmp_player = Player(num=num, strategy=strategy[num], strategy_para=strategy_parameter[num][i],
										income=income[num][i], tax=tax[num][i], start_capital=start_capital[num][i], building_tax=b_tax[num][i])

					tmp.append(tmp_player)
				player_combination.append(tmp)
	elif args.mode == 2:
		player_combination = []
		para_list = [args.strategy_parameter, args.income, args.tax, args.start_capital, args.building_tax]
		para_combination = generate_combination(5, para_list)
		for p in para_combination:
			tmp = []
			for i in range(num_of_players):
				tmp.append(Player(num=i, strategy=args.strategy[0], strategy_para=p[0],
												income=p[1], tax=p[2], start_capital=p[3], building_tax=p[4]))
			player_combination.append(tmp)
	else:
		raise ValueError("Unknown type.")
	return player_combination


def single_simulation(players, num):
	last = time.time()
	cur_simulation_dic = {"settings": {}, "details": {}, "results": {}}
	player_info_lst = []
	for i in range(len(players)):
		cur_player_dic = {
			"strategy": players[i].strategy,
			"strategy_para": players[i].strategy_para,
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
			dev_print("{} out of {} simulation of current combination finished.".format(i, args.number))

	# r.addHitResults(g.board.hits)

	# Calculate the amount of simulations per second
	now = time.time()
	duration = now - last
	avg_time = duration / args.number
	try:
		avg_round = total_rounds / valid_simulation
	except ZeroDivisionError:
		avg_round = float("inf")

	cur_simulation_dic["results"]["num"] = num
	cur_simulation_dic["results"]["avg_time"] = avg_time
	cur_simulation_dic["results"]["avg_round"] = avg_round
	cur_simulation_dic["results"]["total_time"] = duration
	cur_simulation_dic["results"]["end_percent"] = valid_simulation / args.number
	# speed = i / (now - start)
	dev_print("ended: ", valid_simulation)
	dev_print("avg_time: ", avg_time)
	dev_print("avg_round: ", avg_round)
	return cur_simulation_dic


def run_simulation_single_process(player_combinations):
	count = 1

	simulation_list = []

	start = time.time()
	for idx, players in enumerate(player_combinations):
		cur_simulation_dic = single_simulation(players, idx)
		dev_print("{} out of {} combination finished.".format(count, len(player_combinations)))
		count += 1
		simulation_list.append(cur_simulation_dic)
	end = time.time()
	metadata_dic["simulations"] = simulation_list
	metadata_dic["simulations_time"] = end - start
	prod_print(json.dumps(metadata_dic) + "\n")
	# Print that the simulation is finished
	dev_print("\nDone!")
	dev_print("\ntotal_time:", metadata_dic["simulations_time"])


def run_simulation_multiprocess(player_combinations, number_of_process):

	simulation_list = []

	def log_result(result):
		dev_print("combination {} finished, {} in total.".format(result["results"]["num"], len(player_combinations)))
		simulation_list.append(result)

	start = time.time()
	pool = mp.Pool(number_of_process)

	for idx, players in enumerate(player_combinations):
		pool.apply_async(single_simulation, args=(players, idx + 1), callback=log_result)
		# cur_simulation_dic = single_simulation(players)
		# dev_print("{} out of {} combination finished.".format(count, len(player_combinations)))
		# simulation_list.append(cur_simulation_dic)
	pool.close()
	pool.join()
	end = time.time()
	metadata_dic["simulations"] = simulation_list
	metadata_dic["simulations_time"] = end - start
	prod_print(json.dumps(metadata_dic) + "\n")
	# Print that the simulation is finished
	dev_print("\nDone!")
	dev_print("\ntotal_time:", metadata_dic["simulations_time"])


def get_plot(args):
	if args.__dict__["change_variable"] is not None:
		para_to_plot = args.__dict__[args.__dict__["change_variable"]]
		simulations = metadata_dic["simulations"]
		if args.mode != 2:
			x = [para_to_plot[0] + para_to_plot[1] * i for i in range(int(para_to_plot[2]))]
		else:
			x = para_to_plot
		y_round = []
		y_time = []
		y_end_percent = []
		y_total_time = []
		for simulation in simulations:
			y_time.append(simulation["results"]["avg_time"])
			y_round.append(simulation["results"]["avg_round"])
			y_end_percent.append(simulation["results"]["end_percent"])
			y_total_time.append(simulation["results"]["total_time"])
		plt.subplot(411)
		plt.plot(x, y_time)
		plt.ylabel("avg_time")
		plt.subplot(412)
		plt.plot(x, y_round)
		plt.ylabel("avg_round")
		plt.subplot(413)
		plt.plot(x, y_end_percent)
		plt.ylabel("end_percent")
		plt.subplot(414)
		plt.plot(x, y_total_time)
		plt.ylabel("total_time")
		plt.show()


def main(args):
	player_combinations = generate_player_combination(args)
	if args.number_of_process == 1:
		run_simulation_single_process(player_combinations)
	else:
		run_simulation_multiprocess(player_combinations, args.number_of_process)
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

	parser.add_argument("-s", "--strategy", type=int, nargs="+", default=[0],
						help="the strategy that players use to buy/upgrade buildings and trade, one for each")

	parser.add_argument("-s_para", "--strategy_parameter", type=float, nargs="+", default=[0, 0, 1],
						help="the strategy that players use to buy/upgrade buildings and trade, one for each")

	parser.add_argument("-v", "--verbose", const=True, action="store_const",
						help="if turned on, generate a full log")

	parser.add_argument("-mode", "--mode", type=int, default=0, choices=[0, 1, 2, 3],
						help="mode 1: linear compare\nmode 2: cross compare uniform players.\nmode 3: cross compare different players")

	parser.add_argument("-n_process", "--number_of_process", type=int, default=1,
						help="number of process used to run this program.")
	parser.add_argument("-plot", "--change_variable", default=None)
	args = parser.parse_args()

	valid, args = check_validity_and_broadcast(args)
	if valid:
		# Run simulation
		main(args)
	else:
		raise ValueError("parameter input not valid, please use -h option for help.")
	if not is_prod:
		get_plot(args)
