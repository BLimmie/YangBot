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
	def __init__(self, condition, output):
		"""
		Sets the condition of the condition_wrapper
		"""
		self.condition = condition
		self.output = output
	def check(self, message):
		"""
		Checks the message against the condition and returns None if false, output if true
		"""
		if self.condition(message):
			return self.output
		return None

def list_check(message, conditions):
	"""
	Takes a list of condition wrappers
	returns the output of the first wrapper that is true
	"""
	result = None
	for condition in conditions:
		result = condition.check(message)
		if result is not None:
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
	test1 = condition_wrapper(returns_true, "This should output")
	test2 = condition_wrapper(returns_false, "This should not output")
	print(list_check("test",[test1]))
	assert (list_check("test",[test1]) == "This should output")
	print(list_check("test",[test1,test2]))
	assert (list_check("test",[test1,test2]) == "This should output")
	print(list_check("test",[test2]))
	assert (list_check("test",[test2]) is None)