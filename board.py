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
		self.hits[tile] += 1

	def getSize(self):
		return (len(Board.TILES_REAL_ESTATE) + len(Board.TILES_CHANCE) +
				len(Board.TILES_COMMUNITY) + len(Board.TILES_UTILITIES) +
				len(Board.TILES_TRANSPORT) + len(Board.TILES_TAX) +
				len(Board.TILES_NONE) + len(Board.TILES_JAIL) +
				len(Board.TILES_GO_TO_JAIL) + len(Board.TILES_GO))