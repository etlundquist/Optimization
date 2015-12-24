#-----------------------------------------------------------------------
# MacPherson Refrigeration Limited Case Study as a MIP Problem in Python
# Author: Eric Lundquist 
# Date Started: 07NOV2015
#-----------------------------------------------------------------------

from pulp import *

# create a list of months which will be the main index for all decision variables and a month number:name dictionary

MONTHS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
MDICT  = {1:'JAN', 2:'FEB', 3:'MAR',  4:'APR',  5:'MAY',  6:'JUN', 7:'JUL', 8:'AUG', 9:'SEP', 10:'OCT', 11:'NOV', 12:'DEC'}

# create constants to store the ACTUAL costs associated with different decisions
# NOTE: these will be used to calculate the objective function value (total production costs) for post-optimal analysis

HIRECOST_A = 1800 # cost of hiring a new worker in a given month
FIRECOST_A = 1200 # cost of firing a worker in a given month
RGWKCOST_A = 2400 # monthly cost of a regular-time worker
OTWKCOST_A = 5700 # monthly cost of an overtime worker
INVTCOST_A = 8    # monthly cost of storing an appliance in inventory

# create constants to store the MODEL costs associated with different decisions
# NOTE: these will be used to attempt to model some of the non-monetary costs associated with certain decisions
# NOTE: to influence how the optimization model will behave. these are the costs entering the model

HIRECOST_M = HIRECOST_A + 0    # add/subtract additional "costs" associated with hiring workers
FIRECOST_M = FIRECOST_A + 0    # add/subtract additional "costs" associated with firing workers
RGWKCOST_M = RGWKCOST_A + 0    # add/subtract additional "costs" associated with regular-time workers
OTWKCOST_M = OTWKCOST_A + 0    # add/subtract additional "costs" associated with overtime workers
INVTCOST_M = INVTCOST_A + 0    # add/subtract additional "costs" associated with inventory storage

# create constants to store non-cost constraint information about the problem

RGWKPROD  = 40     # the number of appliances a non-OT worker can make in a month
OTWKPROD  = 80     # the number of appliances an OT worker can make in a month
MAXPROD   = 13000  # the total max production capacity of the plant in a given month
SHIPMENTS = {1:4400, 2:4400, 3:6000, 4:8000, 5:6600, 6:11800, 7:13000, 8:11200, 9:10800, 10:7600, 11:6000, 12:5600}
# shipment forecast by month - this is the demand we have to meet via some combination of production and inventory 

# create variables to store STARTING INFORMATION about the problem (values at the end of the last year)

STARTWK   = 160 # we start with 160 workers at the plant as of the beginning of the year
STARTINVT = 240 # we start with 240 appliances in inventory as of the beginning of the year

# create sets of DECISION VARIABLES indexed by month for each key monthly decision in the problem

hires      = LpVariable.dicts('HIRE', MONTHS, 0, None, 'Integer')
fires      = LpVariable.dicts('FIRE', MONTHS, 0, None, 'Integer')
rgworkers  = LpVariable.dicts('RGWK', MONTHS, 0, None, 'Integer')
otworkers  = LpVariable.dicts('OTWK', MONTHS, 0, None, 'Integer')
tlworkers  = LpVariable.dicts('TLWK', MONTHS, 0, None, 'Integer')
production = LpVariable.dicts('PROD', MONTHS, 0, None, 'Integer')
inventory  = LpVariable.dicts('INVT', MONTHS, 0, None, 'Integer')

# create a new LpProblem object for the problem

prob = LpProblem('MacPherson Refrigeration', LpMinimize)

# add the OBJECTIVE FUNCTION (minimize costs) to the problem
# NOTE: write this as a sum of monthly costs using the lpSum() function

prob += lpSum([HIRECOST_M*hires[m]     + 
               FIRECOST_M*fires[m]     + 
               RGWKCOST_M*rgworkers[m] + 
               OTWKCOST_M*otworkers[m] + 
               INVTCOST_M*inventory[m] for m in MONTHS]), "Total Cost of Production"

# add the PROBLEM CONSTRAINTS to the problem
# NOTE: do this within a big loop over months - need to add constraints for identity relationships 
# involving decision variables both within month and between months

for m in MONTHS:

    # CONSTRAINTS THAT REFERENCE STARTING INFORMATION ABOUT THE PROBLEM

    if (m == 1):

        prob += production[m] + STARTINVT >= SHIPMENTS[m], "Shipment Requirement Month 1"
        prob += inventory[m] == STARTINVT + production[m] - SHIPMENTS[m], "Inter-Month Inventory Identity Month 1"
        prob += tlworkers[m] == STARTWK   + hires[m] - fires[m], "Inter-Month Workers Identity Month 1"

    # CONSTRAINTS THAT REFERENCE THE PREVIOUS MONTH

    else:

        prob += production[m] + inventory[m-1] >= SHIPMENTS[m], "Shipment Requirement Month {0}".format(m)
        prob += inventory[m] == inventory[m-1] + production[m] - SHIPMENTS[m], "Inter-Month Inventory Identity Month {0}".format(m)
        prob += tlworkers[m] == tlworkers[m-1] + hires[m] - fires[m], "Inter-Month Workers Identity Month {0}".format(m)

    # CONSTRAINTS THAT DEPEND ONLY ON INFORMATION FROM THE CURRENT MONTH

    prob += production[m] <= MAXPROD, "Plant Production Limit Month {0}".format(m) 
    prob += production[m] <= RGWKPROD*rgworkers[m] + OTWKPROD*otworkers[m], "Worker Production Limit Month {0}".format(m)
    prob += tlworkers[m] == rgworkers[m] + otworkers[m], "Worker Type Identity Month {0}".format(m)

    # CONSTRAINTS ADDED DURING POST-OPTIMAL ANALYSIS
    #-----------------------------------------------
    
    # PLAN 1: CONSTANT WORKFORCE WITH CONSTANT PRODUCTION
    # NOTE: you cannot get a more optimal solution under these constraints
    # if (m > 1): prob += hires[m] == 0
    # prob += fires[m] == 0
    # prob += otworkers[m] == 0
    # prob += production[m] == RGWKPROD*rgworkers[m]

    # PLAN 2: CONSTANT WORKFORCE WITH VARYING PRODUCTION AND NO INVENTORY
    # NOTE: you can get a more optimal solution under these constraints
    # if (m > 1): prob += hires[m] == 0
    # prob += fires[m] == 0
    # prob += inventory[m] == 0

    # PLAN 3: VARYING WORKFORCE WITH VARYING PRODUCTION AND NO INVENTORY OR OVERTIME
    # NOTE: you can get a more optimal solution under these constraints
    # prob += otworkers[m] == 0
    # prob += inventory[m] == 0

    # PLAN 4: FIX A MINIMUM INVENTORY REQUIREMENT AND DON'T ALLOW FIRING ANYONE
    # NOTE: this is $323k worse than "optimal"
    # prob += inventory[m] >= 1000
    # prob += otworkers[m] <= rgworkers[m]
    # prob += fires[m] == 0

# write the LP formulation to a text file and attempt to solve the problem

prob.writeLP("MacPherson.lp")
prob.solve()

# calculate the objective function value using the ACTUAL costs instead of the MODEL costs

totalcost = 0
for m in MONTHS:
    totalcost += HIRECOST_A * hires[m].varValue
    totalcost += FIRECOST_A * fires[m].varValue
    totalcost += RGWKCOST_A * rgworkers[m].varValue
    totalcost += OTWKCOST_A * otworkers[m].varValue
    totalcost += INVTCOST_A * inventory[m].varValue

# write the problem solution information to both the console and an external text file

try:

    fh = open('MacPhersonResults.txt', mode = 'w')
    print("Solution to MacPherson Refrigeration Production Schedule Problem")
    print("Problem Status: {0}".format(LpStatus[prob.status]))
    print("Total Model Production Cost = {0:7.0f} | Total Actual Production Cost = {1:7.0f} | Difference = {2:8.2f}".format(value(prob.objective), totalcost, value(prob.objective)-totalcost))
    print("")

    fh.write("Solution to MacPherson Refrigeration Production Schedule Problem\n")
    fh.write("Problem Status: {0}\n\n".format(LpStatus[prob.status]))
    fh.write("Total Model Production Cost = {0:7.0f} | Total Actual Production Cost = {1:7.0f} | Difference = {2:8.2f}\n".format(value(prob.objective), totalcost, value(prob.objective)-totalcost))
    fh.write("Fixed Model Costs: Hire = {0} Fire = {1} Reg = {2} Ovt = {3} Inv = {4}\n".format(HIRECOST_M,FIRECOST_M,RGWKCOST_M,OTWKCOST_M,INVTCOST_M))
    fh.write("\n")

    for m in MONTHS:

        l1 = "{0}: ".format(MDICT[m])
        l2 = "Hires = {0.varValue: <2.0f} Fires = {1.varValue: <2.0f} ".format(hires[m], fires[m])
        l3 = "RegularTime Workers = {0.varValue: <3.0f} OverTime Workers = {1.varValue: <3.0f} ".format(rgworkers[m], otworkers[m])
        l4 = "Total Workers = {0.varValue: <3.0f} Production = {1.varValue: <5.0f} ".format(tlworkers[m], production[m])
        l5 = "Inventory = {0.varValue: <5.0f}".format(inventory[m])

        print(l1 + l2 + l3 + l4 + l5)
        fh.write(l1 + l2 + l3 + l4 + l5 + "\n")

except IOError:
    print('failed to write results to external text file')
finally:
    if fh: fh.close()



