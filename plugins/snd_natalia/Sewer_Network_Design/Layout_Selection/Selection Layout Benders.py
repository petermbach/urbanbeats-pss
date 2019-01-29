from gurobipy import *

manholes = range(20)
tipe = [1,2]
W = 999999999999
scen=[0,1]
cost = {'p':3, 'q':1, 'r':10}

arcs, length = multidict({
(0,1):100,
(1,2):100,
(2,3):100,
(0,4):100,
(1,5):100,
(2,6):100,
(3,7):100,
(4,5):100,
(5,6):100,
(6,7):100,
(5,10):100,
(6,11):100,
(7,12):100,
(8,9):100,
(9,10):100,
(10,11):100,
(11,12):100,
(8,13):100,
(9,14):100,
(10,15):100,
(12,17):100,
(13,14):100,
(14,15):100,
(15,16):100,
(16,17):100,
(17,18):100,
(18,19):100,
(1,0):100,
(2,1):100,
(3,2):100,
(4,0):100,
(5,1):100,
(6,2):100,
(7,3):100,
(5,4):100,
(6,5):100,
(7,6):100,
(10,5):100,
(11,6):100,
(12,7):100,
(9,8):100,
(10,9):100,
(11,10):100,
(12,11):100,
(13,8):100,
(14,9):100,
(15,10):100,
(17,12):100,
(14,13):100,
(15,14):100,
(16,15):100,
(17,16):100,
(18,17):100,
(19,18):100,
})


b={}
b[0]=[0.03435,0.0618,0.0574,0.0339,0.03435,0.07985,0.0776,0.0541,0.0346,0.06275,0.0889,0.064,0.05745,0.0294,0.06075,0.07425,0.0487,0.06325,0.0213,-1.0387]
b[1]=[0.0227,0.0704,0.0782,0.0327,0.0521,0.0617,0.0692,0.0704,0.0606,0.0873,0.0409,0.0825,0.0287,0.0591,0.0348,0.0842,0.0588,0.0385,0.0490,-1.0818]

print(b[scen[1]][19])
LB, UB, CUT = {},{},{}

result = open ("Resultados.txt","w")


def Callback_2ndStage(M, where):
    
    if where == GRB.Callback.MIPSOL:
        M._LB.append(M.cbGet(GRB.Callback.MIPSOL_OBJ))
        x_hat={}
        z_hat={}
        
        for var in M._vars:
            if (var.VarName[0]=='x'):
                name=var.VarName.split(',')
                
                a=name[0].split('(')
                c=name[2].split(')')
               
                
                t=int(c[0])
                j=int(name[1])
                i=int(a[1])
                x_hat[i,j,t]= M.cbGetSolution(var)
            if (var.VarName[0]=='z'):
                s=int(var.VarName[-1])
                z_hat[s]= M.cbGetSolution(var)
        SP,OF = {},{}        
        for s in M._scen:
            
            result.write("Escenario:" + str(s) + "\n")
            SP[s] = Model("SP"+str(s))
            SP[s].setParam('OutputFlag', 0)
            
            y = {(i,j,t):SP[s].addVar(vtype=GRB.CONTINUOUS,obj=100,name="y_"+str((i,j,t))) for i,j in M._arcs for t in M._tipe}
                
            '''#Constraints
                #Balance
            '''
            SP[s].addConstrs((quicksum(y[i,j,t] for i,j in M._arcs.select(i,'*') for t in M._tipe)-quicksum(y[k,i,t] for k,i in M._arcs.select('*',i) for t in M._tipe)==b[s][i]) for i in M._manholes)
                        
            '''Límite inferior para el flujo '''
            for i,j in M._arcs:
               for t in M._tipe:
                    SP[s].addConstr(x_hat[i,j,t]*(b[s][i]/4)<=y[i,j,t])
        
            '''Límite superior para el flujo '''
            for i,j in M._arcs:
                for t in M._tipe:
                    SP[s].addConstr(y[i,j,t]<=W*x_hat[i,j,t]) 
                    
            suma=0
            for k in b[s]:
                if k != b[s][len(b[s])-1]:             
                    suma+=k
            SP[s].addConstr(y[len(M._manholes)-2,len(M._manholes)-1,2]==suma)
            
            '''Restricción de flujo para las tuberías de inicio'''        
            for i in M._manholes:
               if i<M._manholes[len(M._manholes)-1]:
                   SP[s].addConstr(quicksum(y[i,j,1] for i,j in M._arcs.select(i,'*'))<=b[s][i])
            
            SP[s].optimize()
         
                
            
            O = {(i,j,t) for i,j,t in x_hat if x_hat[i,j,t]<.5}
            I = {(i,j,t) for i,j,t in x_hat if x_hat[i,j,t]>.5}
            
            for i,j in M._arcs:
                for t in M._tipe:
                    result.write(str(y[i,j,t])+"\n")
                    result.write(str(x_hat[i,j,t]))
           
            expresOFF=[]
            expresON=[]
            expresOBJ=[]
            for var in M._vars:
                if (var.VarName[0]=='x'):
                    name=var.VarName.split(',')
                    a=name[0].split('(')
                    c=name[2].split(')')     
                    t=int(c[0])
                    j=int(name[1])
                    i=int(a[1])
                    if((i,j,t) in O):
                        expresOFF.append(var)
                    if ((i,j,t) in I):
                        expresON.append(1-var)
                        
                if (var.VarName[0]=='z'):
                    if (int(var.VarName[-1]) == s):
                        expresOBJ.append(var)
            
            if(GRB.INFEASIBLE):
                
                OFF = quicksum(expresOFF)
                ON = quicksum(expresON)
                M.cbLazy( OFF + ON,  GRB.GREATER_EQUAL, 1)
                M._cuts += 1
                M.update()
              
            else:

                OF[s]= SP[s].ObjVal                           
                OFF = quicksum(expresOFF)
                ON = quicksum(expresON)
                OBJ = quicksum(expresOBJ)
                
                TERM = (OF[s]-max(M._LB))
                M.cbLazy(OBJ+TERM*(OFF+ON), ">", OF[s])
                M.update()
                M._cuts += 1
                
        M._CUT.append(M._cuts)
        if not M._UB:
            aux = 1e8
        else:
            aux = M._UB[-1]
        if (M._LB[-1] - sum(z_hat.values()) + sum(OF.values())) < aux:
            M._UB.append(M._LB[-1] - sum(z_hat.values()) + sum(OF.values()))
        else:
            M._UB.append(aux)
            
       # x_hat = {int(var.VarName[-1]):M.cbGetSolution(var) for var in M._vars if var.VarName[0]=='x'}
       # z_hat = {int(var.VarName[-1]):M.cbGetSolution(var) for var in M._vars if var.VarName[0]=='z'}
        	
  #  else:
  #      print("NO")

def CallbackDeco1(manholes, scen, arcs, b, cost, tipe):
    m=Model("Master")
    m._L=0
    m._cuts=0
    m._CUT=[]
    m._LB=[]
    m._UB=[]
    
    m._manholes=manholes
    m._arcs=arcs
    m._b=b
    m._cost=cost
    m._tipe=tipe
    m._scen=scen
    m.setParam('OutputFlag', 0)
    m.Params.lazyConstraints= 1
    
    x = {(i,j,t):m.addVar(vtype=GRB.BINARY,obj=cost['p'],name="x_"+str((i,j,t))) for i,j in m._arcs for t in m._tipe}
    z = {s:m.addVar(vtype=GRB.CONTINUOUS,name="z_"+str(s), obj=1) for s in m._scen}
    m.update()
   
    
    #Constraints
    
    '''Restricción de tuberías por tramo'''
    for i,j in arcs:
        m.addConstr(quicksum(x[i,j,t]+x[j,i,t] for t in tipe)==1)
        
    m.addConstr(x[len(manholes)-2,len(manholes)-1,2]==1)
    
    
    '''Restricción de tuberías de salida por pozo'''
    for i in manholes:
        if i < manholes[-1]:
             m.addConstr((quicksum(x[i,j,2] for i,j in arcs.select(i,'*'))==1))
    
    '''Restricción de conexiones entre tuberías adyacentes'''
    for i in manholes:
        if i < manholes[-1]:
            m.addConstr(quicksum(x[j,i,t] for j,i in m._arcs.select('*',i) for t in m._tipe )<=W*quicksum(x[i,k,2] for i,k in m._arcs.select(i,'*')))
            m.addConstr(quicksum(x[j,i,t] for j,i in m._arcs.select('*',i) for t in m._tipe )>=quicksum(x[i,k,2] for i,k in m._arcs.select(i,'*')))
    
    
        
    m._vars=m.getVars()
    m.update()       
    m.optimize(Callback_2ndStage)
    
    for i,j in m._arcs:
        for t in m._tipe:
            print(x[i,j,t])
            
    print(z[0].varName[-1])
    print(z[1])
    print(m._b)        
    
   # m._LB.append(m.objVal)
   # m._UB.append(m.objVal)
   # m._CUT.append(m._CUT[-1])
    
    
    return 2
	
    
a = CallbackDeco1(manholes, scen, arcs, b, cost, tipe) 
  
print (a)	
result.close
    
	
    

#LB['c'], UB['c'], CUT['c'] = CB.CallbackDeco(stores, clients, scen, cap, cost)