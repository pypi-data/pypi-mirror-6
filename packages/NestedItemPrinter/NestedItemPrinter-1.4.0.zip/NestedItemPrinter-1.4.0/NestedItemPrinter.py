"""This module is a simple function for printing all elements in a list"""
import sys
def printer(some_list, indent=False, tabswitch=0, fh=sys.stdout):
	"""The function recursively prints all 
	elements (even other lists) in a list"""
	for each_item in some_list:
		if isinstance(each_item, list):
			printer(each_item, indent, tabswitch+1, fh)
		else:
			if indent:
				for tab_stop in range(tabswitch):
					print("\t",end='',file=fh)
			print(each_item, file=fh)
