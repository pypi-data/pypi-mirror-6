#!/usr/bin/env python3
# Google Code Jam Input Parser & Output Formatter (GCJ I/O)
# by Kye W. Shi

from os.path import splitext, exists

# Jam from direct input ("raw" jam)
class RawJam():
	def __init__(self, input):
		self._lines = input.strip().split('\n')

		self.T = int(self._lines[0]) # T test cases
		del self._lines[0]
		self._sort()

		self._solution = lambda x: x
	def __repr__(self):
		return '<gcjio.RawJam object at %s (%d test cases)>' % (hex(id(self)), self.T)

	# Methods to separate test cases & convert types
	def _simplify(self, x): # Try to convert to intended (semantic) type
		for fn in [int, float]:
			try:
				return fn(x)
			except ValueError: pass
		else: return x
	def _sort(self): # Main organizing method
		# Find pattern in line structures
		semantic = [] # Semantically typed lines (intended variable types)
		structures = [] # Recognized structure
		pattern = [] # Line structure pattern
		for line in self._lines:
			items = [self._simplify(item) for item in line.split(' ')]
			structure = [type(item) for item in items]

			if len(items) == 1: items = items[0]
			semantic.append(items)


			if structure in structures: # Previously used structure
				pattern.append(structures.index(structure))
			else: # Not found
				pattern.append(len(structures))
				structures.append(structure) # Add to recognized

		# Split into "chunks"
		indices = [] # Beginning line indices of each "chunk"
		try:
			prev = 0
			while True:
				index = pattern.index(0, prev)
				prev = index + 1
				indices.append(index)
		except ValueError: pass
		indices.append(len(self._lines)) # Last chunk, index to end

		chunks = [semantic[indices[i]:indices[i+1]] if indices[i+1]-indices[i] > 1 else semantic[indices[i]] for i in range(len(indices) - 1)]
		size = len(chunks) // self.T # Number of chunks per case

		if size == 1: self.cases = chunks # Single chunk (not in array) per case, to prevent messiness
		else: self.cases = [chunks[i:i+size] for i in range(0, len(chunks), size)] # Group chunks into cases
		return self.cases

	# Set method that solves problem per case
	def solve(self, solution):
		self._solution = solution # `solve` will be called with parameter being case array

	# Output (and save to file) solutions in GCJ format (Case #n: solution)
	def output(self): # `stdout`: whether to print to stdout
		return '\n'.join('Case #%d: %s' % (i+1, self._solution(self.cases[i])) for i in range(self.T))

# Jam from input file, not direct input
class Jam(RawJam):
	def __init__(self, path):
		self._path = path
		self._lines = open(path, 'r').read().strip().split('\n')

		self.T = int(self._lines[0]) # T test cases
		del self._lines[0]
		self._sort()

		self._solution = lambda x: x
	def __repr__(self):
		return '<gcjio.Jam object at %s (%d test cases)>' % (hex(id(self)), self.T)

	# Output (and save to file) solutions in GCJ format (Case #n: solution)
	def output(self, save=False, path=None, overwrite=False): # `stdout`: whether to print to stdout
		y = '\n'.join('Case #%d: %s' % (i+1, self._solution(self.cases[i])) for i in range(self.T))

		# Save to file
		if save: # Save file
			if not path: path = splitext(self.path)[0] + '.out' # No path specified, change extension to .out
			if exists(path) and not overwrite:
				print('File exists, use `overwrite = True` to overwrite!')
			elif overwrite: open(path, 'w+').write(y)
			else: open(path, 'a').write(y)

		print(y)
		return y
