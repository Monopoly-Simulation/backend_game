# Monopoly simulation

This is a simulation program written in Python to simulate games of Monopoly.
The goal of this project is to determine a set of parameters which can allow the game
to last as long as possible.
## Parameter List
```
usage: monopoly.py [-h] [-n] [-p {1 to 100}] [-mode {1,2,3}] [-r ROUNDS] [-s {0,1,2}]
[-s_para input] [-tax input] [-b_tax input] [-i input] [-sc input] 

Programm to simulate the game of Monopoly.

optional arguments:
  -h, --help            show this help message and exit
  -n NUMBER, --number NUMBER
                        number of simulations to run
  -p {1 to 100}, --players {1 to 100}
                        number of players to run the simulation with
  -mode {1,2,3} --mode
                        the mode the program will run with, each mode has different requirements on input
  -r ROUNDS, --rounds ROUNDS
                        maximum rounds each game can last
  -s {0,1,2}, --strategy
                        the strategy each player will use when buying/upgrading a house or trading
  -s_para input, --strategy_parameter
                        the strategy parameter according to the strategy chosen, can be a decimal between 0 and 1(for strategy 1)
  or a constant(for strategy 2) 
  
  -tax input, --tax 
                        If input as a decimal between 0 and 1, it means the percentage tax chared
  on a player's cash when passing [go]. If input as a number bigger then 1, it means a head tax charged 
  independent of cash when passing [go]

  -b_tax input, --building_tax
                        a percetage tax charged on player's property when passing [go]
  -sc input, --start_capital
                        the money for each player when the game starts
  -income input, --income
                        the money each player can get when passing [go]
  -v, --verbose
                        a flag, if turned on the program can generate a log.txt file that record import events in the simulation.

```

The input format for `input` above is as follows:

It can be only one number, meaning that only one value for that variable will be used when generating combination.

It can be 3 numbers, `[start, step, number]`, meaning that all values in `[start, start + step, ..., start + step * (number - 1)]` will
be used when generating combination, values are the same for different players.

It can be (3 * n) numbers, n is the number of players, `[start1, step1, number1,..., startn, stepn, numbern]`, meaning that 
`[starti, starti + stepi, ..., starti + stepi * (numberi - 1)]` will be used for playeri when generating combinations.

The way how the combinations are generated differs according to different modes.

## Player Strategy
Monopoly game involves a lot of trading actions. This program allows three different strategy the players 
can use to decide whether or not to trade/buy/upgrade.

strategy 0: A player can choose to buy/sell a land randomly, 50% yes and 50% no. This is the default one. 
                      
strategy 1: A player can make his/her decisions on the basis that he/she is always trying to keep his/her cash above a certain value. 
For example, if the boundary is set to 100, and if buying a certain house will make his/her cash below 100, then he/she will choose not to buy it, 
and if he/she is fined, making his/her cash below 100, he/she will choose to sell a house to try to make his/her cash above 100.                   

strategy 2: A player can make his/her decisions on the basis that he/she is always trying to keep his/her cash above a percentage of his/her total property, 
that is his/her cash plus the value of all his/her lands. For example, let's set the boundary to 0.1. If the player now has 100 cash and his/her lands worth 900, 
then his/her cash counts for exactly 10% of his/her total property. In this case, he/she will not try to buy other houses until he/she gets extra money 
because doing so will cause the cash percentage to be lower than 10%, and if he/she is fined he/she will also sell a house because any fine will cause 
the cash percentage to be lower than 10% and he/she needs to sell a house to make his/her cash percentage be higher than 10% again. 

Note: All these actions are set on the precondition that a player will never let his/her cash lower than 0

##Different Modes
The program has three different running mode: mode 1, mode 2 and mode 3. 

#### Mode 1
Mode 1 means that each parameter should be passed using range mode, and linear combination is used. For example, if income is passed
as `[100, 50, 2]` and tax is passed as`[0, 0.1, 2]`, combinations `[income, tax]` in `[[100, 0], [150, 0.1]]` will be simulated. Note that 
`number` should be the same for all variables in this mode. Player customization is allowed in this mode.

#### Mode 2
Mode 2 will generate cross combinations between different parameters while keeping all the players in one simulation having the same
parameters. Using the same example from above, then combinations `[income, tax]` in `[[100, 0], [150, 0], [100, 0.1], [150, 0.1]]` will be simulated.
Player customization is not allowed in this mode.

#### Mode 3
Mode 3 is similar to Mode 2, but allows the user to customize players and cross comparison will also be conducted on 
player parameters. For example, if player 1 and 2 both have income in `[100, 150]`, then combinations `[player 1 income, player 2 income]` in 
`[[100, 100], [100, 150], [150, 100], [150, 150]]` will be simulated. Alert: this mode may generate too many combinations and you should avoid using
this mode unless necessary.


