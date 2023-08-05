"""
	Copyright 2013 Jose Maria Miotto (josemiotto+datagram@gmail.com)

	This file is part of datagram.

	datagram is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	datagram is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with datagram.  If not, see <http://www.gnu.org/licenses/>.
"""

from Histogram import *
from Distribution import *
import scipy.optimize

"""
Auxiliary functions for the Generalized Pareto Distribution fitting function implemented from Grimshaw, Technometrics 35 (2) 1993, pags. 185-191.
"""

def h(data,theta):
	x = np.array([ 1.0-theta*z[0] for z in data ])
	y = np.array([ z[1] for z in data ])
	N    = sum( y )
	wlog = sum( y*np.log(x) )/N
	w1m  = sum( y/x )/N
	hf   = ( 1.0 + wlog )*w1m - 1.0
	return hf

def dh(x,y,theta):
	x1 = 1.0-theta*x
	N    = sum( y )
	wlog = sum( y*np.log(x1) )/N
	w1   = sum( y*x1 )/N
	w1m  = sum( y/x1 )/N
	w2m  = sum( y/(x1**2.0) )/N
	hf   = ( 1.0 + wlog )*w1m - 1.0
	hf1  = ( w2m - w1m**2.0 - wlog*(w1m-w2m) )/theta
	d = hf/hf1
	while theta-d>0.0:
		d = d/2.0
	return d

def h2lim(m1,m2):
	return m2-2.0*m1**2.0



"""
	General functions to fit, there are many options.
"""






def fit(hist,fit_type,**kwargs):
	"""
	Method to fit a distribution, given by 'fit_type'; kwargs are the necessary parameters for the given distribution.
	"""
	try:
		hist.fits
	except:
		hist.fits = {}

	if fit_type == 'pareto':
		threshold = kwargs['threshold']
		idx = next(i for i,z in enumerate(hist.x) if z>threshold)
		x = hist.x[idx:]-threshold
		y = hist.hist[idx:]
		N = np.sum(y)
		m1 = np.sum( y*x )/N
		m2 = np.sum( y*x**2.0 )/N
		eps = 1e-6/m1
		xmin = min(x)
		xmax = max(x)
		theta_L = 2.0*(xmin-m1)/xmin**2.0
		theta_U = 1.0/xmax-eps
		h2 = h2lim(m1,m2)
		if h2>0.0:
			theta = theta_L
			d = dh(x,y,theta)
			i = 0
			while (abs(d)>eps):
				i += 1
				d = dh(x,y,theta)
				theta -= d
		else:
			print 'h2<0'
			#exit()
			pass
		k = -np.sum(y*np.log(1.0-theta*x))/N
		a = k/theta
		hist.fits['pareto'] = { 'k':k, 'a':a, 'threshold':threshold }

	else:
		print 'The requested Fit Type is currently not supported.'

#k,a,threshold
def fit_np(hist, fit_type, p0, bounds=None, idx=0):
	try:
		hist.fits
	except:
		hist.fits = {}
	X = hist.x[idx:]
	Y = hist.hist[idx:]
	print X[:5]
	print Y[:5]
	#func = lambda p,x,y : -1.0*np.sum(y*distributions[fit_type]['logpdf'](x,p))
	def func(p,x,y):
		z = -1.0*np.sum(y*distributions[fit_type]['logpdf'](x,p))
		#print p,z
		return z
	p0 = np.array(p0)
	parameters, maxlikelihood, d = scipy.optimize.fmin_l_bfgs_b(func, p0, args=(X,Y,), bounds=bounds, approx_grad=True)
	hist.fits[fit_type] = {x:parameters[i] for i,x in enumerate(distributions[fit_type]['parameters'])}




"""
	Functions for Statistical Assesment of the fits.
"""


#def KS_statistics(hist,fit_type):
	#"""
	#Compute the Kolmogorov Smirnov statistic for the distribution given by fit_type. Requires a previous fit.
	#"""
	#p = hist.fits[fit_type]
	#idx = next(i for i,z in enumerate(hist.x) if z>p['threshold'])
	#x = hist.x[idx:]-p['threshold']
	#y = hist.ccdf[idx:] # CCDF
	#if fit_type == 'pareto':
		#fit = y[0]*(1.0-x*p['k']/p['a'])**(1.0/p['k']) # CCDF
	#else:
		#print 'The requested Fit Type is currently not supported.'
	#KS = abs(fit-y)
	#hist.fits[fit_type]['KS_D'] = np.amax(KS)

def KS_statistics(hist,dist):
	"""
	Compute the Kolmogorov Smirnov statistic for the distribution given by fit_type. Requires a previous fit.
	"""
	p = dist.parameters
	idx = next(i for i,z in enumerate(hist.x) if z>p['threshold'])
	x = hist.x[idx:-1]
	y = hist.ccdf[idx:]# CCDF
	KS = np.abs(y-y[0]*dist.ccdf(x))
	d = np.amax(KS)
	return d
