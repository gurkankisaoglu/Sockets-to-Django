from Test.phase1testcases import *
from Database import Database
from pymongo.errors import ServerSelectionTimeoutError

#TO RUN THESE TESTS HAVE A MONGOD RUNNING IN THE BACKGROUND
# mongod --dbpath ./data/db

if __name__ == '__main__':
	try:
		Database.dbclient.drop_database("img_tool_db")
	except ServerSelectionTimeoutError:
		print("MongoDB is offline, try running with mongod --dbpath ./data/db settings.")
		exit(-1)

	"""Image Testings"""
	Test0()
	Test1()
	Test2()
	Test3()
	Test4()
	Test5()
	Test6()
	Test7()
	Test8()
	Test9()
	Test10()
	Test11()
	Test12()
	Test13()
	Test14()
	Test15()
	Test16()
	Test17()
	Test18()
	Test19()
	Test20()
	print()
	print("END OF TESTS")
