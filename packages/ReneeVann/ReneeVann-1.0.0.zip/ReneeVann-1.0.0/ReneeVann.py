"""this is a 
             module."""
def print_abc(the_list):
	"you can print a lol list in this function"
	for each in the_list:
		if isinstance(each,list):
			print_lol(each)
		else:
			print(each)

