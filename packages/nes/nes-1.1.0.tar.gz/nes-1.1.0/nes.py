"""
The folowing fundtion parse 
a list to single elements
"""
def print_lol (the_list,level):
	for i in the_list:
		if (isinstance(i,list)):
			print_lol(i, level+1)
		else:
			for tab_stop in range (level):
				print ("\t",end="")
			print (i)

"""
Calling
the
function
"""
