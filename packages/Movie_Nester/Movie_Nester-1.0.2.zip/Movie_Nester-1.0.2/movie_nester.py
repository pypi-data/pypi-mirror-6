def process_list (details):
	for eachitem in details:
		if isinstance(eachitem,list):
			process_list(eachitem)
		else:
			print(eachitem)
