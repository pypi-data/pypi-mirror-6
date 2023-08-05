"""no comment"""
def print_l(the_list):
	for each in the_list:
		if isinstance (each,list):
			print_l(each)
		else:
			print(each)


			
