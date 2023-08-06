"""This module is a simple function for printing all elements in a list"""

def printer(some_list):
	"""The function recursively prints all 
	elements (even other lists) in a list"""
	for each_item in some_list:
		if isinstance(each_item, list):
			printer(each_item)
		else:
			print(each_item)