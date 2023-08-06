def print_lol(the_list, indent = False, level = 0):
	for each_items in the_list:
		if isinstance(each_items, list):
			print_lol(each_items, indent, level + 1)
		else:
			if indent :
				for tab_stop in range(level):
					print "\t",
			print each_items
