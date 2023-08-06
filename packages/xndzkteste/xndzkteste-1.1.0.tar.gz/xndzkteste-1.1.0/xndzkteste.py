def print_lol(the_list, level):
	"""the_list é qualquer tipo de lista do python e level é usado para inserir tabulações"""
	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol(each_item, level+1)
		else:
			for tab_stop in range(level):
				print("\t", end="")				
			print(each_item)