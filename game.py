from util import *
from board import *
from chance import *
from community import *


class Game:

	def __init__(self, players, rounds):
		self.players = players
		self.board = Board()
		self.chancePile = ChancePile()
		self.communityPile = CommunityPile()
		self.rounds = rounds

	def run(self):
		# Play the game for a given amount of rounds
		for i in range(0, self.rounds):
			self.round()

	def round(self):
		# Each round, every player should get its turn
		for player in self.players:
			self.turn(player)

	def turn(self, player):
		# Get number of eyes on dice
		diceResults = diceThrow()
		# Move the player to new position, goingToJail True is 3 doubles thrown
		player.move(self.board, diceResults)

		# Get tile type
		tileType = self.board.getTileType(player.position)

		# Set to go to jail if on 'Go To Jail' tile
		if tileType == "gotojail":
			player.go_to_jail()

		# Do chance card if player has landed on a chance tile
		if player.position in Board.TILES_CHANCE:
			player.doChanceCard(self.chancePile.pullCard(), self.board)

		# Do commmunity card if player has landed on a community chest tile
		if player.position in Board.TILES_COMMUNITY:
			player.doCommunityCard(self.communityPile.pullCard(), self.board)

		# Log the fact that a player has landed on a tile, after all movements
		self.board.hit(player.position)

		# Go again if not on jail and has thrown double
		if tileType != "jail" and diceResults[1]:
			self.turn(player)