import time

class cache:
	'''
	A function-caching decorator class.
	'''

	def __init__(self, max_age, check=None):
		'''
		Initialise a new cache object.
		'''

		self.max_age  = float(max_age)
		self.check    = check if check else lambda: False
		self.expires  = time.time() + self.max_age
		self.function = None
		self.value    = None

	def __call__(self, function):
		'''
		Return a fresh or cached value.
		'''

		def deco(*_, **__):
			if not self.function:
				self.function = function
				self.value    = function()

			if self.expires < time.time() or self.check():
				self.expires = time.time() + self.max_age
				self.value   = function()

			return self.value
		
		deco.cache = self
		return deco
