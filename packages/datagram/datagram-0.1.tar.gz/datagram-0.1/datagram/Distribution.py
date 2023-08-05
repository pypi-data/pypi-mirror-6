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

import numpy as np

distributions = {
	'pareto': { # parameters; k, a threshold
		'parameters': ['k','a','threshold'],
		'pdf':		lambda x,p: (1.0-(x-p[2])*p[0]/p[1])**(1.0/p[0]-1.0)/p[1] ,
		'cdf':		lambda x,p: 1.0-(1.0-(x-p[2])*p[0]/p[1])**(1.0/p[0]) ,
		'ccdf':		lambda x,p: ( 1.0 - (x-p[2])*p[0]/p[1] )**(1.0/p[0]) ,
		'logpdf':	lambda x,p: -np.log(p[1])+(1.0/p[0]-1.0)*np.log(1.0-(x-p[2])*p[0]/p[1])
		},
	'exp': { # parameters; l
		'parameters': ['l'],
		'pdf':		lambda x,p: np.exp(-x*p[0])*p[0],
		'cdf':		lambda x,p: 1.0-np.exp(-x*p[0]),
		'ccdf':		lambda x,p: np.exp(-x*p[0]),
		'logpdf':	lambda x,p: -x*p[0]
		}
	}

class Distribution:

	def __init__(self, name, **parameters):
		self.name = name
		self.parameters = parameters
		self.p = [ self.parameters[z] for z in distributions[self.name]['parameters'] ]

		# Here we parse the functions defined at the beginning for the desired type of distribution.
		for key,val in distributions[self.name].items():
			if key in ['parameters']:
				pass
			else:
				setattr(self, key, lambda x,val=val:val(x,self.p) )

	def prior(self):
		"""Prior distribution of the likelihood"""
		return 1.0
		#s = 0.4 # 2*sigma**2
		#return np.exp(-(self.k+0.3)**2.0/s)/(3.141592*s)**0.5*np.exp(-(self.a-1.2)**2.0/s)/(3.141592*s)**0.5

	def loglikelihood(self, hist, idx=1):
		x = hist.x[idx:]
		y = hist.counts[idx:]
		return np.sum(y*(self.logpdf(x)+np.log(self.prior())))

