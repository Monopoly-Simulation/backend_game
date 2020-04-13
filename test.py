#!/usr/bin/python

from game import *
import random
random.seed(0)

g = Game([Player(1,1,1,1), Player(2,2,2,2), Player(3,0,0,0)], 1000)
g.run()