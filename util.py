from random import randint
import argparse


log = open("logs.txt", "w")
metadata = open("metadata.txt", "w")


verbose = False


def print_verbose():
	print(verbose)


def diceThrow():
	dice1 = randint(1, 6)
	dice2 = randint(1, 6)

	# Return total num of eyes, and whether or not the dices were equal
	return dice1, dice2


def representsInt(s):
	try: 
		int(s)
		return True
	except ValueError:
		return False


def positiveInt(x):
	if not representsInt(x):
		raise argparse.ArgumentTypeError("should be a integer")
	x = int(x)
	if x <= 0:
		raise argparse.ArgumentTypeError("should be bigger than 0")
	return x