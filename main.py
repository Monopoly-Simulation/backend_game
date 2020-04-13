import sys
from objects import Player
from game import Game
import random
random.seed(0)


def run_simulation(args):
    number_of_players = int(args[0])
    rounds = int(args[1])
    player_args = [int(i) for i in args[2:]]
    players = []
    for i in range(number_of_players):
        buying_strategy = player_args[i * 3]
        upgrading_strategy = player_args[i * 3 + 1]
        trading_strategy = player_args[i * 3 + 2]
        players.append(Player(i, buying_strategy, upgrading_strategy, trading_strategy))
    game = Game(players, rounds)
    game.run()


if __name__ == '__main__':
    print()
    run_simulation(args=sys.argv[1:])