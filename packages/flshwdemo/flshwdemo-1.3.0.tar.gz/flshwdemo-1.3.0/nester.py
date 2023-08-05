def print_lol(the_list,indent=false,level=0):
	"""递归打印列表元素，level用来在遇到嵌套列表时插入制表符。"""
	for each_item in the_list:
		if isinstance(each_item,list):
			print_lol(each_item,indent,level+1)
		else:
                        if indent:
                                for tab_stop in range(level):
                                        print("\t",*level,end='')
                        print(each_item)



			
