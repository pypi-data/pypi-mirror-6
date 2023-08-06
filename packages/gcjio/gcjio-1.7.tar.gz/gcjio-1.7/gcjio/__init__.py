#!/usr/bin/env python3
# Google Code Jam Input Parser & Output Formatter (GCJ I/O)
# by Kye W. Shi

from os.path import splitext, exists

# Jam from direct input ("raw" jam)
class RawJam():
	def __init__(self, input, fixed = False):
		self._lines = input.strip().split('\n')

		self.T = int(self._lines[0]) # T test cases
		del self._lines[0]
		self._sort(fixed)

		self._solver = lambda x: x
	def __repr__(self):
		return '<gcjio.RawJam object at %s (%d test cases)>' % (hex(id(self)), self.T)

	# Methods to separate test cases & convert types
	def _simplify(self, x): # Try to convert to intended (semantic) type
		for fn in [int, float]:
			try:
				return fn(x)
			except ValueError: pass
		else: return x
	def _sort(self, fixed): # Main organizing method
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

		if fixed: # Fixed size chunks
			size = len(semantic) // self.T
			chunks = semantic
		else: # Split into chunks from pattern recognition
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
			
			if len(chunks) % self.T != 0: # Failsafe in case doesn't perfectly divide, switch to fixed mode
				chunks = semantic
				size = len(semantic) // self.T
	
		if size == 1: self._cases = chunks # Single chunk (not in array) per case, to prevent messiness
		else: self._cases = [chunks[i:i+size] for i in range(0, len(chunks), size)] # Group chunks into cases
		return self._cases

	def case(index): return self._cases[0] # Get test case by index (zero-indexed)

	# Set method that solves problem per case
	def solve(self, solver):
		self._solver = solver # `solver` will be called with parameter being case array

	# Output (and save to file) solutions in GCJ format (Case #n: solution)
	def output(self):
		output = ''
		for case in range(self.T):
			solution = self._solver(self._cases[case])
			if isinstance(solution, list) or isinstance(solution, tuple): solution = ' '.join(str(i) for i in solution)
			else: solution = str(solution)
			output += 'Case #%d: %s\n' % (case+1, solution)
		output = output.strip()

		print(output)
		return output

# Jam from input file, not direct input
class Jam(RawJam):
	def __init__(self, path, fixed=False):
		self._path = path
		with open(path, 'r') as f:
			self._lines = f.read().strip().split('\n')

		self.T = int(self._lines[0]) # T test cases
		del self._lines[0]
		self._sort(fixed)

		self._solver = lambda x: x
	def __repr__(self):
		return '<gcjio.Jam object at %s (%d test cases)>' % (hex(id(self)), self.T)

	# Output (and save to file) solutions in GCJ format (Case #n: solution)
	def output(self, save=False, path=None, overwrite=False):
		output = super().output()

		# Save to file
		if save: # Save file
			print() # New line for prettiness
			if not path: path = splitext(self._path)[0] + '.out' # No path specified, change extension to .out
			if exists(path) and not overwrite:
				print('File exists, use `overwrite = True` to overwrite!')
				return output, False
			else:
				with open(path, 'w') as f:
					f.write(output)
					print('Successfully saved output to', path)

				return output, True
		else: return output
