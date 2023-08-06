import numpy as np
from scipy import linspace, special
from scipy import factorial as fac
import matplotlib.pyplot as plt


def nOverk(n,k):
    return fac(n,1) / fac(n-k,1) / fac(k,1)

def makeLP_expl(nl,nt):		# explicite method
	t = linspace((-1+1./nt),(1-1./nt),nt)
	P = np.zeros([nl,nt], float)

	P[0,:] = np.ones(nt)

	for n in range(0,nl):
		frontFactor = 1.0/2.**n	
		coeff_arr = np.array([nOverk(n,k)**2 for k in range(n+1)])
		tm1,tp1 = t-1., t+1.
		val_arr = np.array([tm1**(n-k)*tp1**k for k in range(n+1)])
		P[n,:] = frontFactor * np.dot(coeff_arr, val_arr)
	return P

def makeLP_rec(nl,nt):		# recursive method
	t = linspace((-1+1./nt),(1-1./nt),nt)
	P = np.zeros([nl,nt], float)
	P[0,:] = np.ones(nt)

	for n in range(1,nl):
		leg = special.legendre(n)
		y   = leg(t)
		P[n,:] = y
	return P

def LT(y,nl):				# the direct way: scalar products of of input with LPs 
	nt = len(y)				# dim of input = no. of time samples in [-1,1]
	P    = makeLP_expl(nl,nt)		# get Legendre polynomials
	LT_y = np.zeros(nl)			
	for l in range(0,nl):
		LT_y[l]  = (2.*l+1.)*(y*P[l,:]).sum()/nt
	return LT_y 

def iLT(LT_y,nt):
	'''
	call:	iLT(LT_y,nt)
	input:	Legendre spectrum of length nl = len(LT_y), 
	nt:	# samples of the inverse transform 	

	returns the inverse Legendre transform of LT_y (the length of which is nt) 
	'''
	nl = len(LT_y)				# input dim = no. of spectral components
	P = makeLP_expl(nl,nt)			# get Legendre polynomials
	iLT = np.zeros(nt)			#backtransform			
	for l in range(0,nl):
		iLT += (LT_y[l]*P[l,:])
	return iLT


# Matrix of Legendre polynomials coefficients
LM7 = np.matrix( ((1,0,-1,0,3./8.,0,-5./16.), (0,1,0,-3./2.,0,15./8.,0),(0,0,3./2.,0,-30./8.,0,105./16.),\
                        (0,0,0,5./2.,0,-70./8.,0),(0,0,0,0,35./8.,0,-315./16.),(0,0,0,0,0,63./8.,0),(0,0,0,0,0,0,231./16.)) )
LM7inv = LM7.I	# inverse Legendre matrix

def L_Spec_fromAtauViaTaylor(A,tau,nl):
	'''
	call:     LegSpectrum_7comp_fromAtau(A,tau):
	function: calculates the first seven components of the Legendre spectrum of an exponential with given inputs
	input: A, amplitude; tau, time constant of exponential
	output is a reasonable guess, but all but precise !
	'''
	yt = np.zeros( (nl) )	# Taylor series coefficients corresponding to Legendre matrix
	a = -1./tau	
	yt[0] = A
	for n in range(1,nl):
		yt[n] = 1./n*yt[n-1]*a
#
	yT = np.matrix(yt).T 		# Transponieren zum (2 x 1)-Spaltenvektor
	z = np.asarray(LM7inv*yT)
	return z.T[0]


def LT_analtcl(A,tau,nl):
	'''
	call:   LegSpectrum_(A,tau,nl) using the analytical solution for L:
	input: 	A, amplitude; tau, time constant of exponential
	'''
	alf = np.exp(1./tau)
	L = np.ones(nl)
#
	L[0] = A*tau*(alf-1./alf)/2.
	L[1] = 1.5*A*tau*((tau-1)*alf - (tau+1)/alf)
#
	for n in range(1,nl-1):
		L[n+1] = (2*n+3)*(tau*L[n] + L[n-1]/(2.*n-1))
#
	return L

def LT_2analtcl(A1,tau1,A2,tau2,nl):
	'''
	call:   LegSpectrum_(A,tau,nl) using the analytical solution for L:
	input: 	A, amplitude; tau, time constant of exponential
	'''
	alf1 = np.exp(1./tau1)
	alf2 = np.exp(1./tau2)
	L1 = np.ones(nl)
	L2 = np.ones(nl)
	L  = np.ones(nl)
#
	L1[0] = A1*tau1*(alf1-1./alf1)/2.
	L2[0] = A2*tau2*(alf2-1./alf2)/2.	
	L1[1] = 1.5*A1*tau1*((tau1-1)*alf1 - (tau1+1)/alf1)
	L2[1] = 1.5*A2*tau2*((tau2-1)*alf2 - (tau2+1)/alf2)
#
	for n in range(1,nl-1):
		L1[n+1] = (2*n+3)*(tau1*L1[n] + L1[n-1]/(2.*n-1))
	for n in range(1,nl-1):
		L2[n+1] = (2*n+3)*(tau2*L2[n] + L2[n-1]/(2.*n-1))
#
	ind = np.arange(nl)
#	plt.plot(ind,L1,ind,L2)
#	plt.show()
	L = L1 + L2
	return L



