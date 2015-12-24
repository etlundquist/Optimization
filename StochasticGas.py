#-----------------------------------------------------------------------
# Stochastic Gas Supply Problem
# Author: Eric Lundquist 
# Date Started: 17NOV2015
#-----------------------------------------------------------------------

from pulp import *

# enter the probabilities of each scenario

P_NORMAL = 1/3
P_COLD   = 1/3
P_VCOLD  = 1/3

# create a dictionary to store the relevant information for each scenario

S = {1: {"D": 100, "P": 5.00, "SC": 1.00, "Prob": P_NORMAL},
     2: {"D": 150, "P": 6.00, "SC": 1.00, "Prob": P_COLD},
     3: {"D": 180, "P": 7.50, "SC": 1.00, "Prob": P_VCOLD}}

# create a list of tuples to store the relevant period/leaf indexes for the problem variables

I = [(p, l) for p in range(1,4) for l in range(1,10)]

# create a dictionary to store the scenario information (1,2,3) corresponding to each problem index position (p,l)
# NOTE: this is a dictionary where the keys are index position tuples and the values are scenario dictionaries

IS = {}
for t in I:

    # time period 1: scenario 1 for all leaves
    if t[0] == 1: 
        IS[t] = S[1]

    # time period 2: scenario 1 for leaves (1,2,3), scenario 2 for leaves (4,5,6), scenario 3 for leaves (7,8,9)
    elif t[0] == 2:
        if   t[1] in (1,2,3): IS[t] = S[1]
        elif t[1] in (4,5,6): IS[t] = S[2]
        else:                 IS[t] = S[3]

    # time period 3: scenario 1 for leaves (1,4,7), scenario 2 for leaves (2,5,8), scenario 3 for leaves (3,6,9)
    else:
        if   t[1] in (1,4,7): IS[t] = S[1]
        elif t[1] in (2,5,8): IS[t] = S[2]
        else:                 IS[t] = S[3]

# create a new LpProblem and the necessary variables for each (period, leaf) tuple

prob     = LpProblem('Gas Supply', LpMinimize)
BuyUse   = LpVariable.dicts('BuyUse',   I, 0, None, 'Continuous') # gas to buy & sell in each period/scenario
BuyStore = LpVariable.dicts('BuyStore', I, 0, None, 'Continuous') # gas to buy & store in each period/scenario
Storage  = LpVariable.dicts('Storage',  I, 0, None, 'Continuous') # gas in storage at the end of each period/scenario

# add the objective function to the problem: total expected costs over all periods, all scenarios

prob += lpSum([
    (IS[(2,l)]['Prob'] * IS[(3,l)]['Prob']) * 
    lpSum([(BuyUse[(p,l)] + BuyStore[(p,l)])*IS[(p,l)]['P'] + Storage[(p,l)]*IS[(p,l)]['SC'] for p in range(1,4)])
for l in range(1,10)])

# demand and storage constraints for each scenario/period

for l in range(1,10):
    for p in range(1,4):

        if p == 1:
            prob += BuyUse[(p,l)]  >= IS[(p,l)]['D']
            prob += Storage[(p,l)] == BuyStore[(p,l)]
        else:
            prob += BuyUse[(p,l)] + Storage[(p-1,l)] >= IS[(p,l)]['D']
            prob += Storage[(p,l)] == Storage[(p-1,l)] + (BuyUse[(p,l)] - IS[(p,l)]['D']) + BuyStore[(p,l)]

# non-anticipatory constraints in period 1
# there can be only one distinct set of decision variable choices in period 1

for l in range(2,10):
    prob += BuyUse[(1,l)]   == BuyUse[(1,1)]
    prob += BuyStore[(1,l)] == BuyStore[(1,1)]
    prob += Storage[(1,l)]  == Storage[(1,1)]

# non-anticipatory constraints in period 2
# there can be only three distinct sets of decision variable choices in period 2

for l in range(2,4):
    prob += BuyUse[(2,l)]   == BuyUse[(2,1)]
    prob += BuyStore[(2,l)] == BuyStore[(2,1)]
    prob += Storage[(2,l)]  == Storage[(2,1)]

for l in range(5,7):
    prob += BuyUse[(2,l)]   == BuyUse[(2,4)]
    prob += BuyStore[(2,l)] == BuyStore[(2,4)]
    prob += Storage[(2,l)]  == Storage[(2,4)]

for l in range(8,10):
    prob += BuyUse[(2,l)]   == BuyUse[(2,7)]
    prob += BuyStore[(2,l)] == BuyStore[(2,7)]
    prob += Storage[(2,l)]  == Storage[(2,7)]

# write the LP formulation to a text file and attempt to solve the problem

prob.writeLP("GasSupply.lp")
prob.solve()

# print the objective function value and decision variable values for all periods/leaves

print("Total Expected Costs = {0: <8.2f}".format(value(prob.objective)))

for p in range(1,4):
    for l in range(1,10):

        l1 = "Period: {0} Leaf: {1} - ".format(p, l)
        l2 = "BuyUse = {0.varValue: <3.0f} BuyStore = {1.varValue: <3.0f} Storage = {2.varValue: <3.0f}".format(BuyUse[(p,l)], BuyStore[(p,l)], Storage[(p,l)])
        
        if l == 1: print("")
        print(l1 + l2)


