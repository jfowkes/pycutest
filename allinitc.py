"""
Nick's "all in it" test problem (constrained version)

   Source:
   N. Gould, private communication.

   SIF input: Nick Gould, June 1990.

   classification OUR2-AY-4-0
"""
import numpy as np
import math as ma

# objective
def f(x):
	return np.array([
	x[2]-1 + x[0]**2 + x[1]**2 + (x[2]+x[3])**2 + ma.sin(x[2])**2 + x[0]**2*x[1]**2 + x[3]-3 +
	ma.sin(x[2])**2 + (x[3]-1)**2 + (x[1]**2)**2 + (x[2]**2 + (x[3]+x[0])**2)**2 +
	(x[0]-4 + ma.sin(x[3])**2 + x[1]**2*x[2]**2)**2 + ma.sin(x[3])**4
	])

# gradient
def g(x):
	return np.array([
	2*(-4 + 2*x[0] + x[0]*x[1]**2 + x[1]**2*x[2]**2 + 2*(x[0]+x[3]) *
	 (x[2]**2 + (x[0]+x[3])**2) + ma.sin(x[3])**2), 
    2*x[1] * (1 + x[0]**2 + 2*x[1]**2 + 2*x[2]**2 * (-4 + x[0] + x[1]**2 * x[2]**2 + ma.sin(x[3])**2)), 
    1 + 2*(x[2]+x[3]) + 4*x[2] * (x[2]**2 + (x[0]+x[3])**2) + 4*ma.cos(x[2])*ma.sin(x[2]) + 
     4*x[1]**2*x[2] * (-4 + x[0] + x[1]**2*x[2]**2 + ma.sin(x[3])**2), 
    -1 + 2*x[2] + 4*x[3] + 4*(x[0]+x[3])*(x[2]**2 + (x[0]+x[3])**2) + 
     4*ma.cos(x[3])*ma.sin(x[3]) * (-4 + x[0] + x[1]**2*x[2]**2 + 2*ma.sin(x[3])**2)
	])

# Hessian
def H(x):
	return np.array([
	[2*(2 + x[1]**2 + 2*x[2]**2 + 6*(x[0]+x[3])**2), 
	 4*x[1]*(x[0]+x[2]**2), 
     4*x[2]*(x[1]**2 + 2*(x[0]+x[3])), 
     4*(x[2]**2 + 3*(x[0] + x[3])**2 + ma.cos(x[3])*ma.sin(x[3]))
    ],
    [4*x[1]*(x[0] + x[2]**2), 
     2*(1 + x[0]**2 - 8*x[2]**2 + 2*x[0]*x[2]**2 + 6*x[1]**2*(1 + x[2]**4) + 2*x[2]**2*ma.sin(x[3])**2), 
     4*x[1]*x[2]*(-7 + 2*x[0] + 4*x[1]**2*x[2]**2 - ma.cos(2*x[3])), 
     8*x[1]*x[2]**2*ma.cos(x[3])*ma.sin(x[3])
    ],
    [4*x[2]*(x[1]**2 + 2*(x[0]+x[3])), 
     4*x[1]*x[2]*(-7 + 2*x[0] + 4*x[1]**2*x[2]**2 - ma.cos(2*x[3])), 
     2 + 12*x[2]**2 + 8*x[1]**4*x[2]**2 + 4*(x[0] + x[3])**2 + 4*ma.cos(x[2])**2 - 
      4*ma.sin(x[2])**2 + 4*x[1]**2*(-4 + x[0] + x[1]**2*x[2]**2 + ma.sin(x[3])**2), 
     2 + 8*x[2]*(x[0]+x[3]) + 8*x[1]**2*x[2]*ma.cos(x[3])*ma.sin(x[3])
    ], 
    [4*(x[2]**2 + 3*(x[0] + x[3])**2 + ma.cos(x[3])*ma.sin(x[3])),
     8*x[1]*x[2]**2*ma.cos(x[3])*ma.sin(x[3]), 
     2 + 8*x[2]*(x[0]+x[3]) + 8*x[1]**2*x[2]*ma.cos(x[3])*ma.sin(x[3]), 
     4*(1 + x[2]**2 + 3*(x[0]+x[3])**2 + (-3 + x[0] + x[1]**2*x[2]**2)*ma.cos(2*x[3]) - ma.cos(4*x[3]))
    ]	
	])

# constraint
def c(x):
	return np.array([
	 x[0]**2 + x[1]**2 - 1
	])

# Jacobian
def J(x):
	return np.array([
	[2*x[0], 2*x[1], 0, 0]
	])

# Jacobian derivative tensor
def T(x):
	return np.array([[
	[2,0,0,0],
	[0,2,0,0],
	[0,0,0,0],
	[0,0,0,0]
	]])

# Lagrangian (v - lagrange multipliers)
def L(x,v):
	return f(x) + np.dot(v,c(x))

# gradient Lagrangian (v - lagrange multipliers)
def gL(x,v): 
	print v.shape
	print J(x).shape
	return g(x) + np.dot(v,J(x))

# Hessian Lagrangian (v - lagrange multipliers)
def HL(x,v): 
	print v.shape
	print T(x).shape
	return H(x) + np.tensordot(v,T(x),axes=1)
