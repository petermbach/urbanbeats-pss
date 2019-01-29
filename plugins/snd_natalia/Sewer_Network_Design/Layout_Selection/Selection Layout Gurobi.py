
"""
Created on Tue Apr 17 11:10:42 2018
:author: duquevna
"""
from gurobipy import *

manholes = range(10)
pipe_type = [1, 2]          # 1: External pipes (outer-branch), 2: Internal pipes (internal-branch)
M = 999999999999


arcs, length = multidict({
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


b = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, -0.9]
#b=[0.3,0.2,0.1,0.2,0.2,0.1,0.1,0.1,0.1,-1.4]
#b=[0.1,0.1,0.1,0.1,0.2,0.2,0.1,0.2,0.3,-1.4]
#b=[0.03435,0.0618,0.0574,0.0339,0.03435,0.07985,0.0776,0.0541,0.0346,0.06275,0.0889,0.064,0.057,0.0294,0.06075,0.07425,0.0487,0.06325,0.0213,-1.0387]

m = Model("Layout")
#m.setParam('OutputFlag', 0)


x = {(i, j, t): m.addVar(vtype=GRB.BINARY,obj=200,name="x_"+str((i, j, t))) for i,j in arcs for t in pipe_type}
y = {(i, j, t): m.addVar(vtype=GRB.CONTINUOUS,obj=200,name="y_"+str((i,j,t))) for i,j in arcs for t in pipe_type}
print(arcs)
'''#Constraints
    #Balance
'''
m.addConstrs((quicksum(y[i,j,t] for i,j in arcs.select(i,'*') for t in pipe_type) - quicksum(y[k, i, t] for k, i in arcs.select('*', i) for t in pipe_type) == b[i]) for i in manholes)

'''Límite inferior para el flujo '''
for i,j in arcs:
   for t in pipe_type:
        m.addConstr(x[i,j,t]*(b[i]/4)<=y[i,j,t])
        
'''Límite superior para el flujo '''
for i,j in arcs:
    for t in pipe_type:
        m.addConstr(y[i,j,t]<=M*x[i,j,t])
        
''' Restricción de tuberías por tramo '''
for i,j in arcs:
    m.addConstr(quicksum(x[i,j,t] + x[j,i,t] for t in pipe_type) == 1)
    
''' Restricción de tuberías de salida por pozo '''
for i in manholes:
    if i < manholes[len(manholes)-1]:
        m.addConstr((quicksum(x[i,j,2] for i,j in arcs.select(i,'*'))<=1))
    
'''Restricción de conexiones entre tuberías adyacentes'''
for i in manholes:
    if i < manholes[len(manholes)-1]:
        m.addConstr(quicksum(x[j,i,t] for j,i in arcs.select('*',i) for t in pipe_type) <= M * quicksum(x[i, k, 2] for i, k in arcs.select(i, '*')))
        m.addConstr(quicksum(x[j,i,t] for j,i in arcs.select('*',i) for t in pipe_type) >= quicksum(x[i, k, 2] for i, k in arcs.select(i, '*')))

        
'''Restricción de flujo para las tuberías de inicio'''        
for i in manholes:
   if i<manholes[len(manholes)-1]:
       m.addConstr(quicksum(y[i,j,1] for i,j in arcs.select(i,'*'))<=b[i])
        
'''Restricción de sentido de flujo y tipo de tuberia en la descarga'''
m.addConstr(x[len(manholes)-2,len(manholes)-1,2]==1)

'''Restricción de flujo de tubería en la descarga'''
suma=0
for k in b:
    if k != b[len(b)-1]:             
        suma+=k
m.addConstr(y[len(manholes)-2,len(manholes)-1,2]==suma)
        
'''Función objetivo'''
#m.setObjective(200, GRB.MINIMIZE)

m.optimize() 
            
print (manholes[4])
for i,j in arcs:
    for t in pipe_type:
        print(y[i,j,t])
    

for i,j in arcs:
    for t in pipe_type:
        
        print(x[i,j,t])
