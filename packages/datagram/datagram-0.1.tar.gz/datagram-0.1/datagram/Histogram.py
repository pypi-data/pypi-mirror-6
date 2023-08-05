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
import file_handlers as fh
import collections as cs

class AppError(Exception): pass

class NoDataError(AppError):
	em = {	400: 'No data was added to this Histogram. Use the add_data method.',
			}
	def __str__(self):
		return '{}. {}'.format(self.args[0],NoDataError.em[self.args[0]])


class Histogram:
	list = {}

	def __init__(self,name):
		"""
		Creates an object Histogram.
		"""
		self.name = name
		Histogram.list[name] = self
		self.N = 0
		self.counts = cs.Counter()

	def __repr__(self):
		return "Histogram '{}' contains {} entries.".format(self.name, int(self.N))

	def update(self):
		"""
		If data is added, all the existent data containers are updated.
		"""
		for fun in ['ccdf','cdf','pdf','hist']:
			try:
				getattr(self,fun)
			except:
				pass
			else:
				getattr(self,'calc_'+fun)()
				break

		try:
			getattr(self,'counts')
		except:
			pass
		else:
			self.N = float(sum(self.counts.values()))

	def add_data(self,data,datatype='counts',fromfile=False):
		"""
		Adds data to an instance. datatype has to be:
		* 'counts'	for non processed data,	[1,2,1,1,4];
		* 'hist'	for processed counts,	[(1,3),(2,1),(4,1)];
		* 'pdf'		for pdfs,				[(1,0.6),(2,0.2),(4,0.2)];
		* 'cdf'		for cdfs,				[(1,0.6),(2,0.8),(3,1.0)];
		* 'ccdf'	for complementary cdfs,	[(1,0.4),(2,0.2),(3,0.0)].
		If fromfile=True, data is the file location itself.
		"""
		if fromfile:
			data = fh.read_svf(data)
			if len(data[0])==1:
				data = [ int(x[0]) for x in data ]
			else:
				try:
					data = [map(float,map(int,x)) for x in data ]
				except ValueError:
					data = [map(float,x) for x in data]

		if datatype == 'counts':
			data = cs.Counter(data)
			self.counts = self.counts + data
			self.update()
		elif datatype == 'hist':
			data = cs.Counter(dict(data))
			self.counts = self.counts + data
			self.calc_hist()
			self.update()
		else:
			#try:
				#data = [ map(float,map(int,x)) for x in data ]
			#except ValueError:
				#data = [ map(float,x) for x in data ]
			setattr( self, 'x', np.array( [ z[0] for z in data ] ) )
			setattr( self, datatype, np.array( [ z[1] for z in data ] ) )

	def calc_counts(self):
		"""
		Return the counts as a dictionary for fast access.
		"""
		self.counts = cs.Counter(dict(zip(self.x,map(int,self.hist))))
		if self.N==0:
			raise NoDataError(400)

	def calc_hist(self,bins=False):
		"""
		Return the counts as a list ready to write.
		"""
		self.x = np.array(sorted(self.counts.keys()))
		self.hist =  np.array([float(self.counts[k]) for k in self.x])
		self.N = np.sum(self.hist)
		if self.N==0:
			raise NoDataError(400)
		if bins:
			if type(bins)=='list':
				self.x_bin = np.array(bins)
				self.hist_bin = []
				i=-1
				for j,x in enumerate(self.x):
					if x>self.x_bin[i+1]:
						i+=1
						self.hist_bin.append(0)
					self.hist_bin[-1] += self.hist[j]

	def calc_pdf(self,bins=False):
		"""
		Calculates the pdf from hist.
		"""
		try:
			self.hist
		except:
			self.calc_hist()
		self.pdf = self.hist/self.N
		if bins:
			self.pdf_bin = self.hist_bin/self.N

	def calc_cdf(self):
		"""
		Calculates the cdf from pdf.
		"""
		try:
			self.pdf
		except:
			self.calc_pdf()
		self.cdf = np.cumsum(self.pdf)[:-1]

	def calc_ccdf(self):
		"""
		Calculates the ccdf from cdf.
		"""
		try:
			self.cdf
		except:
			self.calc_cdf()
		self.ccdf = 1.0-self.cdf

	def write(self,file_name,prop='hist'):
		"""
		Write the desired property to a file file_name.
		"""
		if prop == 'counts':
			try:
				self.hist
			except:
				self.calc_hist()
			prop = 'hist'
		if (prop == 'cdf') or (prop == 'ccdf'):
			x = self.x[:-1]
		y = getattr(self,prop)
		data = zip(x,y)
		fh.write_svf(file_name, data)