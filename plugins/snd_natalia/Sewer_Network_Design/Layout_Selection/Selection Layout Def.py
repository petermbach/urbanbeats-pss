# -*- coding: utf-8 -*-
"""
Created on Tue Oct 23 11:10:42 2018
@author: duquevna
"""

from gurobipy import *

'''
Input data: 
    Number of manholes 
    Topology (Connectivity between manholes)
    Costs(weight)
    Inflow per manhole b[]
'''
manholes = range(10)    # Set the number of manholes
pipe_type = [1, 2]           # Type 1: outer-branch  2: inner-branch
M = 999999999999        # BIG number

result = open ("Resultados.txt","w")

# Definition of arcs and weight of each arc
# The wight in both directions (i,j) or (j,i) is the same
# and is independent of the type of the pipe
arcs, weight = multidict({
    (0, 1): 100,
    (1, 2): 100,
    (0, 3): 100,
    (3, 4): 100,
    (1, 4): 100,
    (4, 5): 100,
    (2, 5): 100,
    (3, 6): 100,
    (6, 7): 100,
    (4, 7): 100,
    (7, 8): 100,
    (5, 8): 100,
    (8, 9): 100,
    (1, 0): 100,
    (2, 1): 100,
    (3, 0): 100,
    (4, 3): 100,
    (4, 1): 100,
    (5, 4): 100,
    (5, 2): 100,
    (6, 3): 100,
    (7, 6): 100,
    (7, 4): 100,
    (8, 7): 100,
    (8, 5): 100,
    (9, 8): 100,
})

# Inflow per manhole. The last manhole receives the sum of all inflows with a negative value
b = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, -0.9]
# b = [0.3,0.2,0.1,0.2,0.2,0.1,0.1,0.1,0.1,-1.4]
# b = [0.1,0.1,0.1,0.1,0.2,0.2,0.1,0.2,0.3,-1.4]
# b = [0.03435,0.0618,0.0574,0.0339,0.03435,0.07985,0.0776,0.0541,0.0346,0.06275,0.0889,0.064,0.057,0.0294,0.06075,0.07425,0.0487,0.06325,0.0213,-1.0387]


# !declarations
# declarations
# !SET
# N: set of integer    !Set of nodes
# K: set of string    !Set of types of arcs
# Termino1: string
# Termino2: string

# !Parameters
# c: dynamic array(N, N) of real        #Cost of existing arcs
# cI: dynamic array(N, N, K) of real    #pseudo - cost of inicial pipes
# b: array(N) of real                   #Demand / offer of each node
# posX: array(N) of real                #coor x of node i \ in N
# posY: array(N) of real                #coor y of node i \ in N
# e: array(N) of real                   #Elevation of each node
# intercept: array(N, N) of real        #intercept of the F.O. for each arc
#     interceptI: dynamic array(N, N, K) of real    !Intercept  point for the F.O
# !Decision variables
# x: dynamic array(N, N, K) of mpvar    #Binary variable: 1, if arc(i, j) is used with the k type
# y: dynamic array(N, N, K) of mpvar    #Flow in the  arc(i, j) with the k type
#
# FO: linctr                            #Objective Function
#
# time1: real                           #Execution time
#
# end - declarations




# Model name in Gurobi
m = Model("Layout")

# Print summary
m.setParam('OutputFlag', 0)

'''
Decision variables
'''
# Binary decision variable representing the flow direction between adjacent manholes
c = 0
x = {(i, j, t): m.addVar(vtype=GRB.BINARY, obj=200, name="x_" + str((i, j, t))) for i, j in arcs for t in pipe_type}
print(x.values())
# Continuous variable representing the flow rate in each pipe
y = {(i, j, t): m.addVar(vtype=GRB.CONTINUOUS, obj=200, name="y_" + str((i, j, t))) for i, j in arcs for t in pipe_type}
print(arcs)

'''
#Constraints
'''
# Mass balance in the nodes
# Flow In - Flow Out = Storage in the node
m.addConstrs((quicksum(y[i, j, t] for i, j in arcs.select(i, '*') for t in pipe_type) - quicksum(y[k, i, t] for k, i in arcs.select('*', i) for t in pipe_type) == b[i]) for i in manholes)

# Lower bound for the flow rate en each pipe
for i, j in arcs:
    for t in pipe_type:
        m.addConstr(x[i, j, t] * (b[i]/4) <= y[i, j, t])  # the inflow is divided in the 4 assuming 4 adjacent manholes
        
# Upper bound for the flow rate en each pipe
for i, j in arcs:
    for t in pipe_type:
        m.addConstr(y[i, j, t] <= M * x[i, j, t])   # M is a BIG number (no upper limit)
        
# There is only one pipe per section of type t going in a specific direction i,j or j,i
for i, j in arcs:
    m.addConstr(quicksum(x[i, j, t] + x[j, i, t] for t in pipe_type) == 1)
    
# At most one inner-branch can come out from each manhole
for i in manholes:
    if i < manholes[len(manholes)-1]:
        m.addConstr((quicksum(x[i, j, 2] for i, j in arcs.select(i, '*')) <= 1))
    
# Connectivity constraint: ensures that outer-branch and inner-branch pipes always drain into inner-branch pipes
# By definition, an inner-branch pipe cannot drain into an outer-branch pipe
for i in manholes:
    if i < manholes[len(manholes)-1]:
        m.addConstr(quicksum(x[j, i, t] for j, i in arcs.select('*', i) for t in pipe_type) <= M * quicksum(x[i, k, 2] for i, k in arcs.select(i, '*')))
        m.addConstr(quicksum(x[j, i, t] for j, i in arcs.select('*', i) for t in pipe_type) >= quicksum(x[i, k, 2] for i, k in arcs.select(i, '*')))

        
# Maximum flow to be transported by an outer-branch pipe as the inflow coming from the upstream manhole
for i in manholes:
    if i < manholes[len(manholes)-1]:
       m.addConstr(quicksum(y[i, j, 1] for i,  j in arcs.select(i, '*')) <= b[i])
        
# The outfall pipe must be an outer-branch pipe towards the outfall (last manhole)
m.addConstr(x[len(manholes)-2, len(manholes)-1, 2] == 1)

# The outflow hast to be equal to the sum of all inflows
total_flow = 0
for k in b:
    if k != b[len(b)-1]:             
        total_flow += k
m.addConstr(y[len(manholes)-2, len(manholes)-1, 2] == total_flow)

'''
Objective function
'''
c = {}
for i, j in arcs:
    for k in pipe_type:
        if x[i, j, t] is None:
            break
        else:
            c[(i, j)] = 2

# m.setObjective(200, GRB.MINIMIZE)
m.optimize()

# print (manholes[4])
for i, j in arcs:
    for t in pipe_type:
        print(y[i, j, t])

for i, j in arcs:
    for t in pipe_type:
        print(x[i, j, t])


print(m.getObjective())
print(m.printStats())
print(m.objVal)