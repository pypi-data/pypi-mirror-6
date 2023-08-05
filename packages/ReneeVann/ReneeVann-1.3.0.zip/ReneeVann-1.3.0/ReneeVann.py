"""this is a 
             module."""
def print_abc(the_list, indent=False, level=0):
	"you can print a lol list in this function"
	for each in the_list:
		if isinstance(each,list):
			print_abc(each, indent, level+1)
		else:
			if indent:
				print("\t" *level, end='')
			print(each)

