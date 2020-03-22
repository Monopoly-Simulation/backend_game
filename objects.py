from util import log


class Building:

	def __init__(self, name, price):
		self.name = name
		self.owner = None
		self.base_price = price
		self.cur_price = 0
		# level 0 means pure land, level 1 means house, level 2 means hotel
		self.level = 0

	def set_owner(self, player):
		self.owner = player

	def improve(self):
		if self.level <= 1:
			self.cur_price += self.base_price
			self.level += 1


class Player:

	def __init__(self, num):
		self.num = num
		self.position = 0
		self.consecutiveDoubles = 0
		self.consecutive_not_Doubles = 0
		self.at_jail = False
		self.cash = 0
		self.income = 100
		self.building = []
		self.land = 0
		self.house = 0
		self.hotel = 0
		self.debt = 0
		self.bankrupt_status = False

	def go_to_jail(self):
		self.at_jail = True
		self.position = Board.TILES_JAIL[0]

	def go_out_of_jail(self):
		self.at_jail = False
		self.position = Board.TILES_NONE[1]

	def buy_building(self, building):
		assert isinstance(building, Building)

		if building.owner is None:
			if self.cash >= building.base_price:
				self.cash -= building.base_price
				self.building.append(building)
				building.set_owner(self)
				self.land += 1
				log.write("player {0} buys a land on {1}, costs {2}, currently has {3} cash.\n".format(self.num, building.name, building.base_price, self.cash))
			else:
				return False
		else:
			if building.owner.num == self.num:
				if self.cash >= building.base_price:
					self.cash -= building.base_price
					if building.level == 0:
						self.land -= 1
						self.house += 1
						log.write('player {0} upgrades the land on {1} to a house, costs {2}, currently has {3} cash.\n'.format(self.num, building.name, building.base_price, self.cash))
					elif building.level == 1:
						self.house -= 1
						self.hotel += 1
						log.write(
							'player {0} upgrades the house on {1} to a hotel, costs {2}, currently has {3} cash.\n'.format(
								self.num, building.name, building.base_price, self.cash))
					building.improve()
				else:
					return False
			else:
				raise PermissionError("You have no right to upgrade the property.\n")

		return True

	def fine_money(self, building):
		fined = int(building.cur_price * 0.2)
		if self.cash >= fined:
			self.cash -= fined
		else:
			self.debt += fined
		building.owner.cash += fined
		log.write(
			"player {0} lands on player {1}'s property, player {0} gives {2} to player {1}, now player {0} has {3}, player {1} has {4}.\n".format(self.num, building.owner.num, fined, self.cash, building.owner.cash))

	def move(self, board, dice1, dice2):
		# Determine whether to go to jail due to double throws
		if not self.at_jail:
			if dice1 == dice2:
				# Add one to the number of consecutive doubles
				self.consecutiveDoubles += 1

				# Signal to go to jail if 3 doubles in a row
				if self.consecutiveDoubles >= 3:
					self.go_to_jail()
					# Reset consecutive throws
					self.consecutiveDoubles = 0
					log.write("player {0} goes to jail because of 3 consecutive doubles.\n".format(self.num))
					return
			else:
				# Reset consecutive doubles every time different numbers are roled
				self.consecutiveDoubles = 0

			# Calculate new position, overflow if necessary
			newPosition, pass_go = self.getNewPosition(dice1 + dice2, board)

			# gain money when pass Go
			if pass_go:
				self.cash += self.income
				log.write("player {0} gains {1} because of passing Go, currently has {2} cash.\n".format(self.num, self.income, self.cash))
			# Add one to position, if went past jail ？？？
			# if (newPosition >= Board.TILES_JAIL[0] and newPosition < 35) and (
			# 		self.position < Board.TILES_JAIL[0] or self.position > 35):
			# 	newPosition += 1
			#
			if newPosition >= board.TILES_JAIL[0] > self.position:
				newPosition += 1
			# Apply new position
			self.position = newPosition
			log.write("player {0} move to {1}.\n".format(self.num, board.TILE_NAME[self.position]))
		else:
			log.write("player {0} is in jail.\n".format(self.num))
			if dice1 == dice2:
				self.go_out_of_jail()
				log.write("player {0} goes out of jail because of a double.\n".format(self.num))
				return
			else:
				self.consecutive_not_Doubles += 1

			if self.consecutive_not_Doubles >= 3:
				self.cash -= 50
				self.go_out_of_jail()
				self.consecutive_not_Doubles = 0
				log.write("player {0} goes out of jail because of paying 50.\n".format(self.num))

	def getNewPosition(self, offset, board):
		tmp = self.position + offset
		return tmp % board.getSize(), tmp != (tmp % board.getSize())

	def doChanceCard(self, card, board):
		# Check the type of the chance card
		# card for moving
		if card.kind == "advance":
			# Move to next utilities if necessary
			if card.value == "utility":
				# Keep track if suitable utilities is found
				moved = False
				# Go through possible utilities
				for pos in board.TILES_UTILITIES:
					# If player is before current utility, go to that one
					if self.position < pos:
						self.position = pos
						moved = True
						break

				# If not yet moved, go to first utilities in array
				if not moved:
					self.position = board.TILES_UTILITIES[0]

			# Move to next railroad if necessary
			elif card.value == "railroad":
				# Keep track if suitable railroad is found
				moved = False
				# Go through possible railroad
				for pos in board.TILES_TRANSPORT:
					# If player is before current railroad, go to that one
					if self.position < pos:
						self.position = pos
						moved = True
						break

				# If not yet moved, go to first railroad in array
				if not moved:
					self.position = board.TILES_TRANSPORT[0]

			# If negative, thus should move back, do that
			elif card.value <= 0:
				self.position, _ = self.getNewPosition(card.value, board)

			# Move player to given position otherwise
			else:
				self.position = card.value
		# card for get money
		elif card.kind == "cash":
			self.cash += card.value

		# card for tax
		elif card.kind == "tax":
			self.cash -= card.value[0] * self.house + card.value[1] * self.hotel

	def doCommunityCard(self, card, board):
		# Go to given position if card is of the advance kind
		if card.kind == "advance":
			self.position = card.value

	def total_property(self):
		land_value = 0
		for i in self.building:
			land_value += i.cur_price
		return land_value + self.cash

	def bankrupt(self):
		return self.total_property() < self.debt


class Board:

	TILE_NAME = [
		"Go",
		"Mediterranean Avenue",
		"Community Chest",
		"Baltic Avenue",
		"Income Tax",
		"Reading Railroad",
		"Oriental Avenue",
		"Chance",
		"Vermont Avenue",
		"Connecticut Avenue",
		"Just Visiting",
		"In Jail",
		"St. Charles Place",
		"Electric Company",
		"States Avenue",
		"Verginia Avenue",
		"Pennsylvania Railroad",
		"St. James Place",
		"Community Chest",
		"Tennessee Avenue",
		"New York Avenue",
		"Free Parking",
		"Kentucky Avenue",
		"Chance",
		"Indiana Avenue",
		"Illinois Avenue",
		"B & O Railroad",
		"Atlantic Avenue",
		"Ventinor Avenue",
		"Waterworks",
		"Marvin Gardens",
		"Go To Jail",
		"Pacific Avenue",
		"North Carolina Avenue",
		"Community Chest",
		"Pennsylvania Avenue",
		"Short Line",
		"Chance",
		"Park Place",
		"Luxury Tax",
		"Boardwalk"
	]

	TILE_BUILDING = [
		None,
		Building("Mediterranean Avenue", 60),
		None,
		Building("Baltic Avenue", 60),
		None,
		Building("Reading Railroad", 200),
		Building("Oriental Avenue", 100),
		None,
		Building("Vermont Avenue", 100),
		Building("Connecticut Avenue", 100),
		None,
		None,
		Building("St. Charles Place", 140),
		Building("Electric Company", 150),
		Building("States Avenue", 140),
		Building("Verginia Avenue", 160),
		Building("Pennsylvania Railroad", 200),
		Building("St. James Place", 180),
		None,
		Building("Tennessee Avenue", 180),
		Building("New York Avenue", 180),
		None,
		Building("Kentucky Avenue", 220),
		None,
		Building("Indiana Avenue", 220),
		Building("Illinois Avenue", 240),
		Building("B & O Railroad", 200),
		Building("Atlantic Avenue", 260),
		Building("Ventinor Avenue", 260),
		Building("Waterworks", 150),
		Building("Marvin Gardens", 280),
		None,
		Building("Pacific Avenue", 300),
		Building("North Carolina Avenue", 300),
		None,
		Building("Pennsylvania Avenue", 320),
		Building("Short Line", 200),
		None,
		Building("Park Place", 350),
		Building("Luxury Tax", 100),
		Building("Boardwalk", 400)
	]

	TILES_REAL_ESTATE = [1, 3, 6, 8, 9, 12, 14, 15, 17, 19, 20, 22, 24, 25, 27, 28, 30, 32, 33, 35, 38, 40]
	TILES_CHANCE = [7, 23, 37]
	TILES_COMMUNITY = [2, 18, 34]
	TILES_UTILITIES = [13, 29]
	TILES_TRANSPORT = [5, 16, 26, 36]
	TILES_TAX = [4, 39]
	TILES_NONE = [10, 21]
	TILES_JAIL = [11]
	TILES_GO_TO_JAIL = [31]
	TILES_GO = [0]

	def __init__(self):
		# Check if total amount of tiles is correct
		tilesCount = self.getSize()
		if tilesCount != 41:
			print("Game board consists of %i tiles, instead of 41!" % tilesCount)

		# Setup array to keep track of times a player had landed on a tile
		self.hits = [0] * 41

	def getTileType(self, tile):
		# Return a string of the type of tile corresponding with the index given
		if tile in Board.TILES_REAL_ESTATE:
			return "realestate"
		elif tile in Board.TILES_CHANCE:
			return "chance"
		elif tile in Board.TILES_COMMUNITY:
			return "community"
		elif tile in Board.TILES_UTILITIES:
			return "utitlities"
		elif tile in Board.TILES_TRANSPORT:
			return "transport"
		elif tile in Board.TILES_TAX:
			return "tax"
		elif tile in Board.TILES_JAIL:
			return "jail"
		elif tile in Board.TILES_GO_TO_JAIL:
			return "gotojail"
		elif tile in Board.TILES_GO:
			return "go"
		else:
			return "none"

	def hit(self, tile):
		# Increment tile hit count in array
		print(tile)
		self.hits[tile] += 1

	def getSize(self):
		return (len(Board.TILES_REAL_ESTATE) + len(Board.TILES_CHANCE) +
				len(Board.TILES_COMMUNITY) + len(Board.TILES_UTILITIES) +
				len(Board.TILES_TRANSPORT) + len(Board.TILES_TAX) +
				len(Board.TILES_NONE) + len(Board.TILES_JAIL) +
				len(Board.TILES_GO_TO_JAIL) + len(Board.TILES_GO))

