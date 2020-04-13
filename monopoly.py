#!/usr/bin/python
from util import log
from game import *
from results import *
import sys
import time
import argparse
import numpy as np

def runSimulation(args):
	# Init results class for saving the results
	r = Results()
	# Print start message
	print("Starting simulation")

	# Set simluation variables
	start = time.time()

	# Go through set amount of simulations
	for i in range(0, args.number):
		# Start a new game, run it and save the results
		print(args.trading_range)
		print(args.upgrading_range)
		b_range = np.arange(args.buying_range[0], args.buying_range[1], args.buying_range[2])
		u_range = np.arange(args.upgrading_range[0], args.upgrading_range[1], args.upgrading_range[2])
		t_range = np.arange(args.trading_range[0], args.trading_range[1], args.trading_range[2])

		buying_para, upgrading_para, trading_para = 1, 1, 1
		for b in b_range:
			for u in u_range:
				for t in t_range:
					if args.buying_strategy == 0:  # random
						buying_para = 1
					elif args.buying_strategy == 1:  # specified ratio
						buying_para = b
					elif args.buying_strategy == 2:  # constant
						buying_para = args.buying_constant

					if args.upgrading_strategy == 0:  # random
						upgrading_para = 1
					elif args.upgrading_strategy == 1:  # specified ratio
						upgrading_para = b
					elif args.upgrading_strategy == 2:  # constant
						upgrading_para = args.upgrading_constant

					if args.trading_strategy == 0:  # random
						trading_para = 1
					elif args.trading_strategy == 1:  # specified ratio
						trading_para = b
					elif args.trading_strategy == 2:  # constant
						upgrading_para = args.upgrading_constant

					g = Game([Player(i, args.buying_strategy, args.upgrading_strategy, args.trading_strategy,
									 buying_para, upgrading_para, trading_para)\
							  for i in range(args.players)], args.rounds)
		g.run()
		r.addHitResults(g.board.hits)

		# Calculate the amount of simulations per second
		now = time.time()
		speed = i / (now - start)

		# Display the progress every 1/1000 of the way to begin finished
		if (i + 1) % (args.number / 1000) == 0:
			sys.stdout.write("\rCurrently at %s%% done, %s games/second" %
				(str(round((i + 1) / float(args.number) * 100, 1)), str(round(speed, 1))))
			sys.stdout.flush()

	# Print that the simulation is finished
	print("\nDone!")

	# Same the results to a csv
	r.writeHTML(args.number, args.players, args.rounds)


if __name__ == "__main__":
	# Handle command line arguments
	parser = argparse.ArgumentParser(description="Programm to simulate the game\
		of Monopoly.")
	parser.add_argument("-n", "--number", type=positiveInt, default=10000,
		help="number of simulations to run")
	parser.add_argument("-p", "--players", type=int, choices=[1,2,3,4,5,6],
		default=1, help="number of players to run the simulation with")
	parser.add_argument("-r", "--rounds", type=positiveInt, default=100,
		help="number of rounds to simulate each game")
	parser.add_argument("-b", "--buying_strategy", type=int, default=0,
						help="the strategy that players use to buy buildings")
	parser.add_argument("-br", "--buying_range", nargs=3, type=float, default=[0, 1, 1],
						help="[start, end, step")
	parser.add_argument("-bc", "--buying_constant", type=int, default=1000)
	parser.add_argument("-u", "--upgrading_strategy", type=int, default=0,
						help="the strategy that players use to build buildings")
	parser.add_argument("-ur", "--upgrading_range", nargs=3, type=float, default=[0, 1, 1],
						help="[start, end, step")
	parser.add_argument("-uc", "--upgrading_constant", type=int, default=1000)
	parser.add_argument("-t", "--trading_strategy", type=int, default=0,
						help="the strategy that players use to trade]")
	parser.add_argument("-tr", "--trading_range", nargs=3, type=float, default=[0, 1, 1],
						help="[start, end, step")
	parser.add_argument("-tc", "--trading_constant", type=int, default=1000)

	args = parser.parse_args()

	# Run simulation
	runSimulation(args)
