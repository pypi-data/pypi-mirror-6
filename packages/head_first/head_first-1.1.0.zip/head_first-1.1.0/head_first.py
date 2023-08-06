def print_lol(the_list, level):
	for each_items in the_list:
		if isinstance(each_items, list):
			print_lol(each_items, level + 1)
		else:
			for tab_stop in range(level):
				print "\t",
			print each_items
