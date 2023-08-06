import random
import time
from decocache.cache import cache

def test_init():
	'''
	Assert that __init__ sets the appropriate attributes.
	'''

	func = cache(0.1)(random.random)
	assert func.cache.max_age == 0.1
	assert func.cache.check() == False
	assert func.cache.expires - time.time() <= func.cache.max_age
	assert func.cache.function == func.cache.value == None

def test_call():
	'''
	Assert that __call__ correctly initialises and does time/check
	tests on values.
	'''
	 
	func = cache(0.1)(random.random)
	val_a = func() 
	assert val_a == func()
	time.sleep(0.2)
	assert val_a != func()

	chck  = False
	func  = cache(1, lambda:chck)(random.random)
	val_a = func()
	assert val_a == func()
	chck  = True
	assert val_a != func()


