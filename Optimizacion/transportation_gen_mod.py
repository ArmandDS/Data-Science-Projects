
from __future__ import division 
from pyomo.environ import *
import numpy as np
model = AbstractModel()


model.n = Param(within=NonNegativeIntegers)
model.m = Param(within=NonNegativeIntegers)
model.s = Param(within=NonNegativeIntegers)
model.I = RangeSet(1,model.n) 
model.J = RangeSet(1,model.m)

model.v= Param(model.I) #transportation costs per unit
model.c = Param(model.I, model.J) #trasportation cost
model.p = Param(model.J) #price for each market
model.d = Param(model.J) #demand for each market
model.f = Param(model.I, model.J) #maximim transportation capacity
model.M = Param(model.I) #maximum production per factory
model.e =  Var(model.I, model.J, domain=Binary)
# the next line declares a variable indexed by the set J 
#model.x = Var(model.I,model.J, domain=NonNegativeReals)
model.x = Var(model.I, model.J, domain=NonNegativeReals)

#definition of the objective function
#definition of the objective function
def obj_expression(model): 
    return sum(sum(model.x[i,j] for i in model.I)*model.p[j] for j in model.J )- (sum(model.x[i,j]*model.c[i,j] for i in model.I for j in model.J ))-sum(sum(model.x[i,j] for j in model.J)*model.v[i] for i in model.I )

model.OBJ = Objective(rule=obj_expression,sense=maximize )

#Demand constraint
def d_constraint_rule(model, j): # return the expression for the constraint for i
    return sum(model.x[i,j] for i in model.I)>= model.d[j]

# the next line creates one constraint for each member of the set model.J 
model.dem_Constraint = Constraint(model.J, rule=d_constraint_rule)

#maximum transport constraint
def f_constraint_rule(model, i,j): # return the expression for the constraint for i
    return (model.x[i,j] )<= model.f[i,j]*model.e[i,j]

model.tx_Constraint = Constraint(model.I,model.J, rule=f_constraint_rule)


#maximum production constraint
def a_constraint_rule(model, i): # return the expression for the constraint for i
    return sum(model.x[i,j] for j in model.J)<= model.M[i]

model.prod_Constraint = Constraint(model.I, rule=a_constraint_rule)

##Binary constraint rule
def b_constraint_rule(model, i): 
    return (sum(model.e[i,j] for j in model.J)<=model.s )
model.b_Constraint = Constraint(model.I, rule=b_constraint_rule)