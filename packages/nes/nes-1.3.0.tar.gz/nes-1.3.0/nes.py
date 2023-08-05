"""
The folowing fundtion parse 
a list to single elements
"""
def print_lol (the_list,indent=False,level=0):
	for i in the_list:
		if (isinstance(i,list)):
			print_lol(i,indent,level+1)
		else:
			if indent:
				for tab_stop in range (level):
					print ("\t"*indent,end="")
				print (i)

