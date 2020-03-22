from board import *


class Building:

	def __init__(self, price):
		self.owner = None
		self.base_price = price
		self.cur_price = 0
		# level 0 means pure land, level 1 means house, level 2 means hotel
		self.level = 0
		self.bankrupt_status = False

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
			else:
				return False
		else:
			if building.owner.num == self.num:
				if self.cash >= building.base_price:
					self.cash -= building.base_price
					if building.level == 0:
						self.land -= 1
						self.house += 1
					elif building.level == 1:
						self.house -= 1
						self.hotel += 1
					building.improve()
				else:
					return False
			else:
				raise PermissionError("You have no right to upgrade the property.")

		return True

	def fine_money(self, building):
		fined = building.cur_price * 0.2
		if self.cash >= fined:
			self.cash -= fined
		else:
			self.debt += fined
		building.owner.cash += fined

	def move(self, board, diceResults):
		# Determine whether to go to jail due to double throws
		if not self.at_jail:
			if diceResults[1]:
				# Add one to the number of consecutive doubles
				self.consecutiveDoubles += 1

				# Signal to go to jail if 3 doubles in a row
				if self.consecutiveDoubles >= 3:
					self.go_to_jail()
					# Reset consecutive throws
					self.consecutiveDoubles = 0
					return
			else:
				# Reset consecutive doubles every time different numbers are roled
				self.consecutiveDoubles = 0

			# Calculate new position, overflow if necessary
			newPosition, pass_go = self.getNewPosition(diceResults[0], board)

			# gain money when pass Go
			if pass_go:
				self.cash += self.income

			# Add one to position, if went past jail ？？？
			# if (newPosition >= Board.TILES_JAIL[0] and newPosition < 35) and (
			# 		self.position < Board.TILES_JAIL[0] or self.position > 35):
			# 	newPosition += 1
			#
			if newPosition > Board.TILES_JAIL[0] >= self.position:
				newPosition += 1
			# Apply new position
			self.position = newPosition
		else:
			if diceResults[1]:
				self.go_out_of_jail()
				return
			else:
				self.consecutive_not_Doubles += 1

			if self.consecutive_not_Doubles >= 3:
				self.cash -= 50
				self.go_out_of_jail()
				self.consecutive_not_Doubles = 0

	def getNewPosition(self, offset, board):
		tmp = self.position + offset
		return tmp % board.getSize(), tmp == (tmp % board.getSize())

	def doChanceCard(self, card, board):
		# Check the type of the chance card
		# card for moving
		if card.kind == "advance":
			# Move to next utilities if necessary
			if card.value == "utility":
				# Keep track if suitable utilities is found
				moved = False
				# Go through possible utilities
				for pos in Board.TILES_UTILITIES:
					# If player is before current utility, go to that one
					if self.position < pos:
						self.position = pos
						moved = True
						break

				# If not yet moved, go to first utilities in array
				if not moved:
					self.position = Board.TILES_UTILITIES[0]

			# Move to next railroad if necessary
			elif card.value == "railroad":
				# Keep track if suitable railroad is found
				moved = False
				# Go through possible railroad
				for pos in Board.TILES_TRANSPORT:
					# If player is before current railroad, go to that one
					if self.position < pos:
						self.position = pos
						moved = True
						break

				# If not yet moved, go to first railroad in array
				if not moved:
					self.position = Board.TILES_TRANSPORT[0]

			# If negative, thus should move back, do that
			elif card.value <= 0:
				self.position = self.getNewPosition(card.value, board)

			# Move player to given position otherwise
			else:
				self.position = card.value
		# card for get money
		elif card.kind == "cash":
			self.cash += card.value

		# card for tax
		elif card.kind == "tax":
			self.cash -= card.value

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
