from numpy import *
from pylab import *
from scipy.optimize import leastsq
import matplotlib.pyplot as plt
from LegendrePolynomials import *

# = = = = = = = = = = = =  = = = = = = = = = = = =   input data  = = = = = = = = = = = = = = = = = = = = = = = = = = 

simData = 1			# take simulated data (1) or read real data from file (0)
if  simData:			# simulated data: exponential with Poisson noise
	A1, tau1,ofs   = 12.0, 0.6, 0.5
	nt = 1000
	t = linspace(-1+1./nt,1-1./nt,nt)
	y0 = A1*np.exp(-t/tau1) + ofs
	yn = np.random.poisson(y0, nt) 	# noisy exp
#					
else:
	z = np.loadtxt('noisyExp.dat')		# read data from test file 
	t   = z[:,0]						# time points
	yn = z[:,1] 						# amplitudes
	nt = len(t)						# length of vectors in time domain
	Tr = t[nt-1]						# last time point, needed for final rescaling
	t = linspace(-1+1./nt,1-1./nt,nt)		# rescale time axis to (-1,1)

# = = = = = = = = = = = =  = = = = = = finite Legendre transform of input data  = = = = = = = = = = = = = = = = = = = = = 
nl = 15
ind = np.arange(nl)
P  = makeLP_expl(nl,nt)				# get Legendre polynomials ...
psinvP_T = pinv(P.T)					# ... and its transposed pseudoinverse
LT_y = LT(yn,nl)						# take the L-transform of the data

plt.title('Legendre spectrum of data')
plt.plot( ind, LT_y,ind, LT_y,'r*' )
plt.show()

nl = int(raw_input("number of Legendre components to be used: ")) + 1    # last highest good looking component index should be entered
ind = np.arange(nl)
P  = makeLP_expl(nl,nt)				# get Legendre polynomials ...
psinvP_T = pinv(P.T)					# ... and its transposed pseudoinverse
LT_y = LT(yn,nl)						# take the L-transform of the data

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
#      Nonlinear least squares fit of experimental Legendre spectrum to parameter-dependent Legendre spectrum 
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 

def Lspect(ind,pL):	     # get parameter-dependent Legendre spectrum that is to be fitted to the spectrum of the data
	nl = len(ind)
	[A1, tau1,ofs] = pL
	LT_fit = LT_analtcl(A1,tau1,nl)
	LT_fit[0]  += ofs
	return LT_fit		

def residuals(pL, ind, LT_y):	# take the deviation vector between experimentally obtained spectrum and model spectrum
	[A1, tau1, ofs] = pL
	err = LT_y  -  Lspect(ind,pL)
	return err

A1     = 13.									# initial values
tau1  = 0.7	
ofs    = A1/100
pL = [A1, tau1,ofs]

plsq = leastsq(residuals, pL, args=(ind, LT_y))	# scipy NNLSQ fitting routine. FInd parameters such that the chi2-sum of residuals is minimized
A,tau,ofs = plsq[0]
print  "A,tau,ofs: ",  A,tau,ofs 

# = = = = = = = = = = = = = = = = = = = = = = = = = =  output  = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
# = = = = = = = = = = = = = = = = = = = = = =   re-scaling of tau and A = = = = = = = = = = = = = = = = = = = = = = = = = = = =

if not simData:
	t_real     = (t+1)*Tr/2.
	tau_real = tau*Tr/2.
	A_real   = A*exp(1./tau)
	print "tau_real: ", tau_real
	print "A_real: ", A_real

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 

plt.plot( t, yn, t, A*exp(-t/tau)+ofs )
plt.title('Least-squares fit to noisy data')
plt.legend(['Fit', 'Noisy', 'True'])
plt.show()


