def print_list(list_name,level):
	for each_item in list_name:
		if isinstance(each_item,list):
			print_list(each_item,level+1)
		else:
			for tab_stop in range(level):
				print("\t",end='')
			print(each_item)