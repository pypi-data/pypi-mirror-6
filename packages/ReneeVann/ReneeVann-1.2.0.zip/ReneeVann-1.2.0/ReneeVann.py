"""this is a 
             module."""
def print_abc(the_list, level=0):
	"you can print a lol list in this function"
	for each in the_list:
		if isinstance(each,list):
			print_abc(each, level+1)
		else:
			for tab_stop in range(level):
				print("\t", end='')
			print(each)

