cast=["The Holy Grail",1975,"Terry Jones & Terry Gilliam",91,["Graham Chapman",["Michael Palin","John Cleese","Terry Gilliam","Eric Idle","Terry Jones"]]];

def print_lol(the_list,level=0):
	for each_list in the_list:
		if isinstance(each_list,list):
			print_lol(each_list,level+1)
		else:
			for tab_stop in range(level):
				print ("	"),
			print(each_list)
