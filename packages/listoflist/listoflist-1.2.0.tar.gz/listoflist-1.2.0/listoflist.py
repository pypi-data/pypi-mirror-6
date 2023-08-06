def printlol(listinlist, level=0):
	for each_item in listinlist:
		if isinstance(each_item, list):
			printlol(each_item, level + 1)
		else:
			for  tab_stop in range(level):
				print("\t", end='')
			print(each_item)