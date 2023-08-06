def print_lol(the_list):
	for each_items in the_list:
		if isinstance(each_items, list):
			print_lol(each_items)
		else:
			print each_items
