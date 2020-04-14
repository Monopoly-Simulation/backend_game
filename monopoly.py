#!/usr/bin/python

from game import Game
from results import *
import random
import time
import argparse
import numpy as np
random.seed(0)


def check_validity_and_broadcast(args):
	n_players = args.players
	n_t_s = len(args.trading_strategy)
	n_u_s = len(args.upgrading_strategy)
	n_b_s = len(args.buying_strategy)
	n_t_r = len(args.trading_range)
	n_u_r = len(args.upgrading_range)
	n_b_r = len(args.buying_range)
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
	return n_t_s == n_players == n_u_s == n_b_s and n_t_r == n_u_r == n_b_r == n_players * 3, args


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


def runSimulation(args):
	# Init results class for saving the results
	r = Results()
	# Print start message
	print("Starting simulation")

	# Set simluation variables
	start = time.time()
	num_of_players = args.players
	# Go through set amount of simulations
	# Start a new game, run it and save the results
	print(args.trading_range)
	print(args.upgrading_range)
	b_strategy = args.buying_strategy
	u_strategy = args.upgrading_strategy
	t_strategy = args.trading_strategy
	for k in range(num_of_players):
		print(np.arange(args.buying_range[k * 3], args.buying_range[k * 3 + 1], args.buying_range[k * 3 + 2]))
	b_range = [np.arange(args.buying_range[k * 3], args.buying_range[k * 3 + 1], args.buying_range[k * 3 + 2]) for k in
			   range(num_of_players)]
	u_range = [np.arange(args.upgrading_range[k * 3], args.upgrading_range[k * 3 + 1], args.upgrading_range[k * 3 + 2]) for k in
			   range(num_of_players)]
	t_range = [np.arange(args.trading_range[k * 3], args.trading_range[k * 3 + 1], args.trading_range[k * 3 + 2]) for k in
			   range(num_of_players)]
	player_params = [[b_range[k], u_range[k], t_range[k]] for k in range(num_of_players)]
	single_player_param_list = []
	for params in player_params:
		single_player_param_list.append(generate_combination(num=3, params=params))
	single_player_list = []
	for num in range(num_of_players):
		tmp = []
		for p in single_player_param_list[num]:
			tmp.append(Player(num=num, buying_strategy=b_strategy[num], upgrading_strategy=u_strategy[num],
							  trading_strategy=t_strategy[num],
							  buying_para=p[0], upgrading_para=p[1], trading_para=p[2]))
		single_player_list.append(tmp)

	player_combination = generate_combination(num=num_of_players, params=single_player_list)

	count = 0
	for players in player_combination:
		log.write("player combination: " + str(players) + "\n")
		for i in range(0, args.number):
			log.write("simulation number" + str(i) + "\n")
			for n in players:
				n.reset()
			g = Game(players, rounds=args.rounds)
			g.run()

			r.addHitResults(g.board.hits)

		# Calculate the amount of simulations per second
			now = time.time()
			speed = i / (now - start)
		count += 1
		# Display the progress every 1/1000 of the way to begin finished
		print("{} out of {} combination finished.".format(count, len(player_combination)))

	# Print that the simulation is finished
	print("\nDone!")

	# Same the results to a csv
	r.writeHTML(args.number, args.players, args.rounds)


if __name__ == "__main__":
	# Handle command line arguments
	parser = argparse.ArgumentParser(description="Programm to simulate the game\
		of Monopoly.")
	parser.add_argument("-n", "--number", type=int, default=1000,
		help="number of simulations to run")
	parser.add_argument("-p", "--players", type=int, choices=[i for i in range(100)],
		default=1, help="number of players to run the simulation with")
	parser.add_argument("-r", "--rounds", type=int, default=1000,
		help="number of rounds to simulate each game")

	parser.add_argument("-b", "--buying_strategy", type=int, nargs="+", default=[0],
						help="the strategy that players use to buy buildings, one for each")
	parser.add_argument("-br", "--buying_range", nargs="+", type=float, default=[0, 1, 1],
						help="[start, end, step], three params for each player")

	parser.add_argument("-u", "--upgrading_strategy", type=int, nargs="+", default=0,
						help="the strategy that players use to build buildings, one for each")
	parser.add_argument("-ur", "--upgrading_range", nargs="+", type=float, default=[0, 1, 1],
						help="[start, end, step], three for each player")

	parser.add_argument("-t", "--trading_strategy", type=int, nargs="+", default=0,
						help="the strategy that players use to trade, one for each")
	parser.add_argument("-tr", "--trading_range", nargs="+", type=float, default=[0, 1, 1],
						help="[start, end, step], three params for each player")

	parser.add_argument("-v", "--verbose", const=True, action="store_const",
						help="if turned on, generate a full log")

	args = parser.parse_args()

	valid, args = check_validity_and_broadcast(args)
	if valid:
		# Run simulation
		runSimulation(args)
	else:
		raise ValueError("parameter input not valid, please use -h option for help.")
