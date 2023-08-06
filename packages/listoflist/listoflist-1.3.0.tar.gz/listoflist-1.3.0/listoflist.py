def printlol(listinlist, indent = False, level=0):
	for each_item in listinlist:
		if isinstance(each_item, list):
			printlol(each_item, indent, level + 1)
		else:
			if indent:
				for  tab_stop in range(level):
					print("\t", end='')
			print(each_item)