#!/usr/bin/python

from game import *
import random
random.seed(0)

g = Game([Player(1,1,1,1,0.5,0.5,0.5), Player(2,2,2,2,500,500,500), Player(3,0,0,0,500,500,500)], 1000)
g.run()