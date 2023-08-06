def king(shubham,indent=False,level=0):
	for each in shubham:
		if isinstance(each,list) :
			king(each,indent,level+1)
		else :
			if indent :
				print("\t"*level,end='')
			print (each)