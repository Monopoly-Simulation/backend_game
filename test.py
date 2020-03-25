#!/usr/bin/python

from game import *
import random
random.seed(0)

g = Game([Player(1), Player(2), Player(3)], 200)
g.run()