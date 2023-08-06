"""This module is a simple function for printing all elements in a list"""

def printer(some_list, tabswitch):
	"""The function recursively prints all 
	elements (even other lists) in a list"""
	for each_item in some_list:
		if isinstance(each_item, list):
			printer(each_item, tabswitch+1)
		else:
			for tab_stop in range(tabswitch):
				print("\t",end='')
			print(each_item)
