from util import log, diceThrow, dev_print
import util
from objects import Board
from chance import ChancePile
from community import CommunityPile


class Game:

	def __init__(self, players, rounds):
		self.info_dic = {"bankrupt_turn":{}}
		self.players = players
		self.board = Board()
		self.chancePile = ChancePile()
		self.communityPile = CommunityPile()
		self.rounds = rounds
		self.bankrupt_count = 0
		self.cur_round = 0

	def run(self):
		# Play the game for a given amount of rounds
		end = False
		for i in range(0, self.rounds):
			# dev_print("round", i)
			self.cur_round = i
			if util.verbose:
				log.write("round {0}:\n".format(i))
			end = self.round()
			if util.verbose:
				log.write("\n")
			if end:
				break
			# for player in self.players:
			# 	dev_print("player {0}: cash {1}, property {2}".format(player.num, player.cash, player.total_property()))
		if not end:
			self.info_dic["end"] = -1

		return self.info_dic

	def round(self):
		# Each round, every player should get its turn
		for player in self.players:
			if not player.is_bankrupt():
				self.turn(player)
				if player.is_bankrupt():
					player.bankrupt()
					self.info_dic["bankrupt_turn"][player.num] = self.cur_round
					if util.verbose:
						log.write("player {} has bankrupted, return all properties to the bank.\n".format(player.num))
					self.bankrupt_count += 1
			if len(self.players) - self.bankrupt_count <= 1:
				for i in self.players:
					if not i.is_bankrupt():
						if util.verbose:
							log.write("player {} wins\n".format(i.num))
						self.info_dic["bankrupt_turn"][i.num] = -1
						self.info_dic["winner"] = i.num
						self.info_dic["end"] = self.cur_round
				return True
		if util.verbose:
			log.write("\n")
		for player in self.players:
			if util.verbose:
				log.write("player {} has {} cash.\n".format(player.num, player.cash))
		if util.verbose:
			log.write("\n")
		return False

	def turn(self, player):
		# Get number of eyes on dice
		dice1, dice2 = diceThrow()
		if util.verbose:
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

		# equivalent to trading
		for building_to_sell in player.building_to_sell_list:
			for other_player in self.players:
				if not other_player.is_bankrupt():
					boundary = other_player.choose_boundary(other_player.t_strategy, other_player.t_para)
					if other_player != player and other_player.cash - building_to_sell.cur_price >= boundary:
						other_player.cash -= building_to_sell.cur_price
						building_to_sell.set_owner(other_player)
						other_player.building.append(building_to_sell)
						player.cash += int(building_to_sell.cur_price * 0.1)
						if util.verbose:
							log.write("player {0} successfully sell land {1} to player {2}, get the remaining {3}, player {0} currently has {4}, player {1} has {5}.".format(player.num, building_to_sell.name, other_player.num, building_to_sell.cur_price * 0.1, player.cash, other_player.cash))
						break
		player.building_to_sell_list = []

		# Log the fact that a player has landed on a tile, after all movements
		self.board.hit(player.position)

		# Go again if not on jail and has thrown double
		if tileType != "jail" and dice1 == dice2:
			self.turn(player)

	def plot_para(self):
		return self.info_dic.get('end', 10000), self.players[0].income, self.players[0].tax, self.players[0].start_capital

