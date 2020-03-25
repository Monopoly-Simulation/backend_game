from util import *
from objects import *
from chance import *
from community import *


class Game:

	def __init__(self, players, rounds):
		self.players = players
		self.board = Board()
		self.chancePile = ChancePile()
		self.communityPile = CommunityPile()
		self.rounds = rounds
		self.bankrupt_count = 0

	def run(self):
		# Play the game for a given amount of rounds
		for i in range(0, self.rounds):
			log.write("round {0}:\n".format(i))
			end = self.round()
			log.write("\n")
			if end:
				break
			for i in self.players:
				print("player {0}: cash {1}, property {2}".format(i.num, i.cash, i.total_property()))

	def round(self):
		# Each round, every player should get its turn
		for player in self.players:
			if not player.is_bankrupt():
				self.turn(player)
				if player.is_bankrupt():
					player.bankrupt()
					log.write("player {} has bankrupted, return all properties to the bank.\n".format(player.num))

					self.bankrupt_count += 1
			if len(self.players) - self.bankrupt_count == 1:
				for i in self.players:
					if not i.is_bankrupt():
						log.write("player {} wins\n".format(i.num))
				return True

		log.write("\n")
		for player in self.players:
			log.write("player {} has {} cash.\n".format(player.num, player.cash))
		log.write("\n")
		return False

	def turn(self, player):
		# Get number of eyes on dice
		dice1, dice2 = diceThrow()
		log.write("player {0} rolls two dices, {1} and {2}.\n".format(player.num, dice1, dice2))
		# Move the player to new position, goingToJail True is 3 doubles thrown
		player.move(self.board, dice1, dice2)

		# Get tile type
		tileType = self.board.getTileType(player.position)

		# Set to go to jail if on 'Go To Jail' tile
		if tileType == "gotojail":
			player.go_to_jail()

		# Do chance card if player has landed on a chance tile
		elif player.position in Board.TILES_CHANCE:
			player.doChanceCard(self.chancePile.pullCard(), self.board)

		# Do commmunity card if player has landed on a community chest tile
		elif player.position in Board.TILES_COMMUNITY:
			player.doCommunityCard(self.communityPile.pullCard(), self.board)

		elif Board.TILE_BUILDING[player.position] is not None:
			building = Board.TILE_BUILDING[player.position]
			if building.owner is None or building.owner.num == player.num:
				player.buy_building(Board.TILE_BUILDING[player.position])
			elif building.owner is not None and building.owner != player.num:
				fined = int(building.cur_price * 0.2)
				player.fine_money(fined, other=building.owner)

		# Log the fact that a player has landed on a tile, after all movements
		self.board.hit(player.position)

		# Go again if not on jail and has thrown double
		if tileType != "jail" and dice1 == dice2:
			self.turn(player)
