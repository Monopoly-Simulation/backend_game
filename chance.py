import random


class ChanceCard:

	def __init__(self, kind, value):
		self.kind = kind
		self.value = value

	def __str__(self):
		# Return the chance card in a readable form
		return "ChanceCard(%s, %s)" % (self.kind, str(self.value))


class ChancePile:

	CARDS = [
		ChanceCard("advance", 0),
		ChanceCard("advance", 25),
		ChanceCard("advance", 12),
		ChanceCard("advance", "utility"),
		ChanceCard("advance", "railroad"),
		ChanceCard("cash", 50),
		# ChanceCard("escapejail", None)
		ChanceCard("advance", -3),
		ChanceCard("advance", 11),
		ChanceCard("tax", [5, 10]), # 25 for house, 100 for hotel
		ChanceCard("cash", -15),
		ChanceCard("advance", 5),
		ChanceCard("advance", 40),
		# ChanceCard("pay", 50), # pay each player 50
		ChanceCard("cash", 150),
		ChanceCard("cash", 100),
	]

	def __init__(self):
		# Generate an order of chance cards
		self.pile = random.sample(range(0, len(self.CARDS)),
			len(self.CARDS))

	def pullCard(self):
		# Get the card that is currently at the top of the pile
		card = self.pile[0]

		# Generate new pile with picked card at the bottom
		newPile = [None] * len(self.pile)
		for i in range(0, len(self.pile) - 1):
			newPile[i] = self.pile[i + 1]
		newPile[len(newPile) - 1] = card

		# Set the new pile to be the pile
		self.pile = newPile
		
		# Return the card that was originally at the top of the pile
		return self.CARDS[card]

	def __str__(self):
		# Start with calling that is a pile of cards
		string = "PILE OF CHANCE CARDS:\n"

		# Print all the chance cards
		for cardIndex in self.pile:
			string += " - "
			string += str(self.CARDS[cardIndex])
			string += "\n"

		# Return the generated string
		return string
