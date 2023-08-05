"""this is a 
             module."""
def print_abc(the_list, level):
	"you can print a lol list in this function"
	for each in the_list:
		if isinstance(each,list):
			print_lol(each, level+1)
		else:
			print(each)

