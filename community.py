import random


class CommunityCard:

	def __init__(self, kind, value):
		self.kind = kind
		self.value = value

	def __str__(self):
		# Return the chance card in a readable form
		return "CommunityCard(%s, %s)" % (self.kind, str(self.value))


class CommunityPile:

	CARDS = [
		CommunityCard("advance", 0),
		CommunityCard("cash", 200),
		CommunityCard("cash", -50),
		CommunityCard("cash", 50),
		# CommunityCard("escapejail", None),
		CommunityCard("advance", 11),
		# CommunityCard("receive", 50), # from every player
		CommunityCard("cash", 100),
		CommunityCard("cash", 20),
		# CommunityCard("receive", 10), # from every player
		CommunityCard("cash", 100),
		CommunityCard("cash", -100),
		CommunityCard("cash", -150),
		CommunityCard("cash", 25),
		CommunityCard("tax", [10, 20]), # for each [house, hotel]
		CommunityCard("cash", 10),
		CommunityCard("cash", 100)
	]

	def __init__(self):
		# Generate an order of chance cards
		self.pile = random.sample(range(0, len(self.CARDS)), len(self.CARDS))

	def pullCard(self):
		# Get the card that is currently at the top of the pile
		card = self.pile[0]

		# Generate new pile with picked card at the bottom
		for i in range(0, len(self.pile) - 1):
			self.pile[i] = self.pile[i + 1]
		self.pile[-1] = card
		# Set the new pile to be the pile
		
		# Return the card that was originally at the top of the pile
		return self.CARDS[card]

	def __str__(self):
		# Start with calling that is a pile of cards
		string = "PILE OF COMMUNITY CHEST CARDS:\n"

		# Print all the chance cards
		for cardIndex in self.pile:
			string += " - "
			string += str(self.CARDS[cardIndex])
			string += "\n"

		# Return the generated string
		return string
