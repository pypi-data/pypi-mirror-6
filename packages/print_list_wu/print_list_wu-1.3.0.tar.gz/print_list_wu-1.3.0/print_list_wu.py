def print_list(list_name,indent=False,level=0):
	for each_item in list_name:
		if isinstance(each_item,list):
			print_list(each_item,indent,level+1)
		else:
			if indent:
				for tab_stop in range(level):
					print("\t",end='')
			print(each_item)