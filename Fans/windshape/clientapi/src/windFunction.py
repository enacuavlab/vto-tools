
from math import sin, cos, exp, sqrt

class WindFunction(object):
	def __init__(self, literal_function, min=0, max=100):
		self.literal_function = literal_function
		self.min = min
		self.max = max

	def calculate(self, x=0, y=0, t=0):
		exec("result="+str(self.literal_function))
		if result < self.min:
			return self.min
		elif result > self.max:
			return self.max
		return result
