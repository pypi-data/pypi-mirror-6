import sys
def print_lol(the_list, indent = False, level = 0, out = sys.stdout ):
	for each_items in the_list:
		if isinstance(each_items, list):
			print_lol(each_items, indent, level + 1, out )
		else:
			if indent :
				for tab_stop in range(level):
					print ("\t", end = '', file = out)
			print (each_items, file = out )
