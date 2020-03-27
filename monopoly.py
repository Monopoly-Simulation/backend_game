#!/usr/bin/python
from util import log
from game import *
from results import *
import sys
import time
import argparse


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
		g = Game([Player(i, args.buying_strategy, args.upgrading_strategy, args.trading_strategy) for i in range(args.players)], args.rounds)
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
	parser.add_argument("-u", "--upgrading_strategy", type=int, default=0,
						help="the strategy that players use to build buildings")
	parser.add_argument("-t", "--trading_strategy", type=int, default=0,
						help="the strategy that players use to trade")
	args = parser.parse_args()

	# Run simulation
	runSimulation(args)