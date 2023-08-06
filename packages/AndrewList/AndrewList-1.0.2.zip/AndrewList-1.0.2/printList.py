"""Python Test module"""
import sys

def AndrewList(inputList, indent=False, depth=0, out=sys.stdout):
	"""Test method for List print"""
	for sublist in inputList:
		if isinstance(sublist, list):
			AndrewList(sublist, indent, depth+1, out)
		else:
			if indent:
				for tab in range(depth):
					print("\t", end='', file=out)
			print(sublist, file=out)
