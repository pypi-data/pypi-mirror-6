import numpy as np
from pylab import *
from LegendrePolynomials import *
import matplotlib.pyplot as plt

#  - - - - - - - - - - - - - - - - - - - - - - stopped-flow data from Ferdi's lab - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

A = np.loadtxt('noisyExp.dat')			# data for subplot A
x1a = A[:,0]					# time points
nt    = len(x1a)				# length of vectors in time domain
y1a = A[:,1] * 100.				# amplitudes
y1a_min = min(y1a)
y1a_max = max(y1a)	
dely = y1a_max -y1a_min

#  - - - - - - - - - - - - - - - - - - - - - - - Legendre filter: fLT and inverse fLT - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

nl=17						# take a spectrum of
LTy1a  = LT(y1a,nl)			# 17 Legendre components

corner = 5					# take 5 a corner component
LTy1a_up2n = LTy1a[:corner]	# truncate L-spectrum
y1a_back = iLT(LTy1a_up2n,nt) # inverse Legendre transform of truncated L-spectrum to get lowpass-filtered time function

#  - - - - - - - - - - - - - - - - - - - - - - - - plotting  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

makePlot = 1
if makePlot:
	x 	= x1a*0.4				# data are assumed to be in (-1,1)
	x1a	= x - 1
	fig = figure(num=None, figsize=(11.7,7.2), dpi=100, facecolor='w', edgecolor='k')	
	fig.subplots_adjust(wspace=0.3)
	fig.subplots_adjust(hspace=0.4)
	fs  =   14	# font size
	sf1 = fig.add_subplot(1,2,1)		# Sub-Plot 1: rows, columns, plot index
	sf1.text(-0.13, 1.15, 'a', transform=sf1.transAxes, fontsize=20, va='top')
	sf1.set_ylim(0.,2.)
	sf1.set_yticks(arange(0., 1.2, 0.5))			
	sf1.set_xlabel('t')
	sf1.set_ylabel('u [V]',rotation='vertical')	
	sf1.plot(x1a,y1a,'#AAAAAA')	
	sf1.plot(x1a,y1a,'#AAAAAA',x1a,y1a_back,'r')		

	sf2 = fig.add_subplot(1,2,2)		# Sub-Plot 2: rows, columns, plot index
	sf2.text(-0.14, 1.15, 'b', transform=sf2.transAxes, fontsize=20, va='top')	# Sub-Plot label
	nl4=len(LTy1a)
	sf2.set_xlim(-0.9,nl4)
	ind4 = np.arange(nl4)	
	sf2.bar(ind4,LTy1a, align='center', width=0.3,color='#AAAAAA')
	sf2.set_xticks(range(0, nl4, 4))
	sf2.set_yticks(range(-30, 32, 15))
	sf2.set_ylim(ymin=1.2*min(LTy1a), ymax=1.2*max(LTy1a))
	sf2.set_xlabel('k')
	sf2.set_ylabel('L',rotation='horizontal')


printPlot = 0
printPlot = raw_input("write plot to file (0/1)? :")
if printPlot ==  '1':
	F = plt.gcf()
	F.savefig("Fig_LegendreFiltering_1200DPI.png",dpi=1201,format='png')
	F.savefig("Fig_LegendreFiltering_300DPI.png",dpi=301,format='png')

show()


