"""Python Test module"""
def AndrewList(inputList, indent=False, depth=0):
	"""Test method for List print"""
	for sublist in inputList:
		if isinstance(sublist, list):
			AndrewList(sublist, indent, depth+1)
		else:
			if indent:
				for tab in range(depth):
					print("\t", end='')
			print(sublist)
