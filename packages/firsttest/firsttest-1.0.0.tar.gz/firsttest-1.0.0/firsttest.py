movies=['The Holy Grail', 1975, 'Terry jones & Terry Gillians', 91, ['Graham Chapman', ['Michal palin', 'john cheese', 'Terry Gillian', 'Eric Idle', 'Terry jones']]]
def print_lol(the_list):
	for new_item in the_list:
		if isinstance(new_item,list):
			print_lol(new_item)
		else:
			print(new_item)

