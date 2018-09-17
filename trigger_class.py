def contains(message, list_of_phrases):
	"""
	Checks if a message (string) contains all 
	"""
	pass

def contains_phrase(message, phrase):
	"""
	Helper for checking if a phrase is in a message
	"""
	pass

#There needs to be more helper functions as deemed necessary

class condition_wrapper():
	def __init__(self, condition):
		"""
		Sets the condition of the condition_wrapper
		"""
		self.check = condition

	def check(self, message):
		"""
		Checks the message against the condition and returns true or false
		"""
		return self.condition(message)

def list_check(message, conditions):
	"""
	Takes a list of condition wrappers
	and evaluates them all to finally return 
	if it passes all conditions
	"""
	result = True
	for condition in conditions:
		result = condition.check(message)
		if not result:
			return result
	return result

if __name__ == "__main__":
	"""
	Test code
	"""
	def returns_true(message):
		return True

	def returns_false(message):
		return False	
	test1 = condition_wrapper(returns_true)
	test2 = condition_wrapper(returns_false)
	assert (list_check("test",[test1]) == True)
	assert (list_check("test",[test1,test2]) == False)

