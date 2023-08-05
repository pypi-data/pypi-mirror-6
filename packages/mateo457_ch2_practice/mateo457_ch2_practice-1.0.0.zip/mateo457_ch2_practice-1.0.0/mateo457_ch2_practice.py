"Lets put a comment here and see if it works"
def print_lol(the_list):
	"""Let's put a comment here and see if it works"""
	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol(each_item)
		else:
			print(each_item)
