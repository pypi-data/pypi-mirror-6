def print_list(ls,indent=True,level=0):
	'''print(indent,level)'''
	for i in ls:
		if isinstance(i,list):
			print_list(i,indent,level+1)
		else:
			if indent:
					print('\t' * level,end='')
			print(i)
