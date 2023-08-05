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

def read_svf(file_name, char=' '):
	"""
	Reads the file file_name, returning a list that for each line of the file have a list of the strings splitted by char.
	"""
	with open(file_name, 'r') as f:
		lines = [ line.rstrip('\n').split(char) for line in f ]
	return lines

def write_svf(file_name, lines, char=' ', mode='w'):
	"""
	Writes to file_name the list lines joining each list of lines (a single line) via the character char.
	"""
	with open(file_name, mode) as f:
		f.write('\n'.join([char.join(map(str,line)) for line in lines]))
