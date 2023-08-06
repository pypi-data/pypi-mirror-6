"""This module is a simple function for printing all elements in a list"""

def printer(some_list, indent=False, tabswitch=0):
	"""The function recursively prints all 
	elements (even other lists) in a list"""
	for each_item in some_list:
		if isinstance(each_item, list):
			printer(each_item, indent, tabswitch+1)
		else:
			if indent:
				for tab_stop in range(tabswitch):
					print("\t",end='')
			print(each_item)