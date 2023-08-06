import os

def getFiles(dir):
	return os.listdir(dir)

def printx(a):
	print a

def allPrint(a):
	map(printx,a)

if __name__ == "__main__": 
	getFiles('.')
