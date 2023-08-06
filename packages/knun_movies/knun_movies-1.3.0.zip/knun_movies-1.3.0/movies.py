cast=["The Holy Grail",1975,"Terry Jones & Terry Gilliam",91,["Graham Chapman",["Michael Palin","John Cleese","Terry Gilliam","Eric Idle","Terry Jones"]]];
names=["John","Eric",["Cleese","Idle"],"Micheal",["Palin"]]

def print_lol(the_list,indent=False,level=0):
	for each_list in the_list:
		if isinstance(each_list,list):
			print_lol(each_list,indent,level+1)
		else:
			if indent:
				for tab_stop in range(level):
					print ("	"),
			print(each_list)
