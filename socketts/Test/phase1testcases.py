from labeledImage import *
from userGroup import *
import cv2
import os
from pymongo.errors import DuplicateKeyError

#Basic Test For User&Group DB Functionality
def Test0():
	U = userGroup.UserGroup()
	print("Test 0 Begins.")
	print("At the beginning, all DB is empty.")
	print("Adding Groups 1 to 5.")
	print()
	U.addGroup("group1")
	U.addGroup("group2")
	U.addGroup("group3")
	U.addGroup("group4")
	U.addGroup("group5")
	print("groups1-5 added with no users.")
	print()
	print("Adding 3 users belonging to different Groups.")
	U.addUser("user1",["group1","group2"],"password1")
	print("user1, [group1, group2], password1 added")
	U.addUser("user2",["group3","group4"],"password2")
	print("user2","[group3,group4]","password2 added")
	U.addUser("user3",["group5"],"password3")
	print("user3","[group5]","password3 added")
	print()
	print("Every call to addUser should expand the group's 'users_in_list' property")
	try:
		groups = U.getGroups("user2") # Since user2 belongs in group3 and group4
		print("Successfully got groups of user2.")
	except TypeError:
		print("No user named 'user2' This should result in a Fail")

	else:
		if len(groups) != 2: # Since user2 belongs in group3 and group4
			print("Test 0 Fails.User2 belongs to Group 3 and Group 4, ")
		else:
			print("These are all users in Database:")
			U.list_all_users()
			print("These are all groups in Database:")
			U.list_all_groups()
	input("Input anything to continue.")
	print()

	print("Delete group5 from DB")
	U.delGroup("group5")
	print("These are all users in Database:")
	U.list_all_users()
	print("These are all groups in Database:")
	U.list_all_groups()

	print("Delete group4 from DB")
	print()
	input("Input anything to continue.")
	U.delGroup("group4")
	print("These are all users in Database:")
	U.list_all_users()
	print("These are all groups in Database:")
	U.list_all_groups()

	print("Delete user3 from DB")
	print()
	input("Input anything to continue.")

	U.delUser("user3")
	print("These are all users in Database:")
	U.list_all_users()
	print("These are all groups in Database:")
	U.list_all_groups()



	print("Delete user2 from DB")
	print()
	input("Input anything to continue.")
	U.delUser("user2")
	print("These are all users in Database:")
	U.list_all_users()
	print("These are all groups in Database:")
	U.list_all_groups()

	print("These are user1's groups:")
	print()
	input("Input anything to continue.")
	g = U.getGroups("user1")
	for item in g:
		print(item)

	input("Input anything to continue.")
	print()
	print("These are group1's users:")
	u = U.getUsers("group1")
	for item in u:
		print(item)

	input("Input anything to continue.")
	print()
	print("Check if user1 is member of group1")
	print(U.ismember("user1","group1"))

	input("Input anything to continue.")
	print()
	print("Change password of user1 from password1 to password1234")
	U.setPassword("user1","password1234")
	U.list_all_users()
	print()
	input("Press Enter to Continue to Test 1.")

# Empty Class Construction and Set Default Checks
def Test1():
	print()
	print("Test 1 for setting default action")
	t1 = LabeledImage()
	print("Before set default:")
	print(t1.default_action)
	print()
	print("Setting it do DENY")
	t1.setDefault("DENY")
	# TEST 1 SET DEFAULT
	print("After set default:")
	print(t1.default_action)
	if (t1.default_action == "DENY"):
		print("Set Default Works Correctly")
	else:
		print("Set Default Fails")
	print()
	input("Press Enter to Continue to Test 2.")


# Test 2 is written for opening an image from a location
def Test2():
	print()
	print("Test 2 for loading image from a location")
	t2 = LabeledImage()
	cur_work_dir = os.getcwd()
	img_loc = cur_work_dir + "/test_images/" + "t1_image.jpg"
	# print(current_path)
	t2.loadImage(img_loc)
	# img = cv2.imread("t1_image.jpg")
	# cv2.imshow("image",img)

	try:
		if (t2.img != None):
			pass
	except ValueError:
		print("Test 2 Passes")
		t2.showImage()
	else:
		print("Test 2 Fails, Didn't Load Image")


# Test Buffer
def Test3():
	print()
	print("Test 3 for loading image from buffer")
	t3 = LabeledImage()
	cur_work_dir = os.getcwd()
	img_loc = cur_work_dir + "/test_images/" + "t2_image.jpg"

	source_img = cv2.imread(img_loc)

	encoded_img = cv2.imencode(".jpg", source_img)

	t3.setImage(encoded_img)
	# print(type(t3.img))

	try:
		if (t3.img != None):
			pass
	except ValueError:
		print("Test 3 Passes")
		t3.showImage()
	else:
		print("Test 3 Fail,Didn't Load Image")


# Adds Image to DataBASE
def Test4():
	print()
	print("Test 4 for saving image to database")
	t4 = LabeledImage()
	cur_work_dir = os.getcwd()
	img_loc = cur_work_dir + "/test_images/" + "t1_image.jpg"
	# print(current_path)
	t4.loadImage(img_loc)
	try:
		t4.save("trialname")
		print("Test 4 Successfully Writes To DB. Congratulations.")
		print("check DB")
	except DuplicateKeyError as err:
		print("Test 4 Fail.")
		print("Uniqueness condition holds in TEST 4. But this shouldn't happen, since db is empty")
	#input("Press Enter to Continue to Test 5.")

def Test5():
	print()
	print("Test 5 for saving image with duplicate names")
	t5 = LabeledImage()
	cur_work_dir = os.getcwd()
	img_loc = cur_work_dir + "/test_images/" + "t1_image.jpg"
	# print(current_path)
	t5.loadImage(img_loc)
	try:
		t5.save("trialname")
		print("Test 5 Fail. Successfully Writes To DB, this shouldn't happen.")
		print("Uniqueness fails in TEST 5. Check indexing constraints.")
	except DuplicateKeyError as err:
		print(err)
		print("Test 5 Success. Error is given due to correctly set uniqueness condition.")
	#input("Press Enter to Continue to Test 6.")


def Test6():
	Database.dbclient.drop_database("img_tool_db")
	print()
	print("Test 6 for updating image when adding rules")
	t6 = LabeledImage()
	cur_work_dir = os.getcwd()
	img_loc = cur_work_dir + "/test_images/" + "t1_image.jpg"
	# print(current_path)
	t6.loadImage(img_loc)
	try:
		t6.save("trialname")
		print("Test 6 Successfully Writes To DB with empty rule list")
	except DuplicateKeyError as err:
		print(err)
		print("This shouldnt happen.")

	t6.addRule("u:user1",("CICLE",100,200,100),"ALLOW")
	t6.load("trialname")
	if len(t6.rule_list)==1:
		print("Successfully updated image when rule added")
		print("check DB")
	else:
		print("Test6 Fails")



def Test7():  # DENY Crop Testing
	print()
	print("Test 7 for DENY & Rules:")

	t7 = LabeledImage()
	cur_work_dir = os.getcwd()
	img_loc = cur_work_dir + "/test_images/" + "t1_image.jpg"
	# print(current_path)
	t7.loadImage(img_loc)
	t7.addRule("u:testuser1", ("RECTANGLE", 100, 100, 200, 200), "DENY")
	for rule in t7.rule_list:
		print(rule)
	t7.getImage("testuser1")


def Test8():  # BLUR Crop Testing
	print()
	print("Test 8 for Blur & Rules:")
	t8 = LabeledImage()
	cur_work_dir = os.getcwd()
	img_loc = cur_work_dir + "/test_images/" + "t1_image.jpg"
	# print(current_path)
	t8.loadImage(img_loc)
	t8.addRule("u:testuser1", ("RECTANGLE", 100, 100, 300, 300), "BLUR")
	for rule in t8.rule_list:
		print(rule)
	t8.getImage("testuser1")


def Test9():  # DEFAULT BLUR
	print()
	print("Test 9 for Default action BLUR")
	t2 = LabeledImage()
	cur_work_dir = os.getcwd()
	img_loc = cur_work_dir + "/test_images/" + "t1_image.jpg"
	# print(current_path)
	t2.loadImage(img_loc)
	t2.setDefault("BLUR")
	t2.getImage("testuser1")


def Test10():  # DEFAULT DENY
	print()
	print("Test 10 for Default action DENY")
	t2 = LabeledImage()
	cur_work_dir = os.getcwd()
	img_loc = cur_work_dir + "/test_images/" + "t1_image.jpg"
	# print(current_path)
	t2.loadImage(img_loc)
	t2.setDefault("DENY")
	t2.getImage("testuser1")


def Test11():  # Circle Deny
	print()
	print("Test 11 for Circular DENY & Rules are:")
	t8 = LabeledImage()
	cur_work_dir = os.getcwd()
	img_loc = cur_work_dir + "/test_images/" + "t1_image.jpg"
	# print(current_path)
	t8.loadImage(img_loc)
	t8.addRule("u:testuser1", ("CIRCLE", 100, 100, 100), "DENY")
	for rule in t8.rule_list:
		print(rule)
	t8.getImage("testuser1")


def Test12():  # Polyline Deny
	print()
	print("Test 12 for Polyline DENY & Rules are:")
	t8 = LabeledImage()
	cur_work_dir = os.getcwd()
	img_loc = cur_work_dir + "/test_images/" + "t1_image.jpg"
	# print(current_path)
	t8.loadImage(img_loc)
	t8.addRule("u:testuser1", ("POLYLINE", [(100, 100), (100, 200), (200, 200)]), "DENY")
	for rule in t8.rule_list:
		print(rule)
	t8.getImage("testuser1")


def Test13():  # Circle BLUR
	print()
	print("Test 13 for Circular BLUR & Rules are:")
	t8 = LabeledImage()
	cur_work_dir = os.getcwd()
	img_loc = cur_work_dir + "/test_images/" + "t1_image.jpg"
	# print(current_path)
	t8.loadImage(img_loc)
	t8.addRule("u:testuser1", ("CIRCLE", 100, 100, 100), "BLUR")
	for rule in t8.rule_list:
		print(rule)
	t8.getImage("testuser1")


def Test14():  # Polyline BLUR
	print()
	print("Test 14 for Polyline BLUR & Rules are:")
	t8 = LabeledImage()
	cur_work_dir = os.getcwd()
	img_loc = cur_work_dir + "/test_images/" + "t1_image.jpg"
	# print(current_path)
	t8.loadImage(img_loc)
	t8.addRule("u:testuser1", ("POLYLINE", [(300, 300), (100, 300), (300, 100)]), "BLUR")
	for rule in t8.rule_list:
		print(rule)
	t8.getImage("testuser1")


def Test15():  # checks if rules are followed in correct order
	print()
	print("Test 15 for check if rules are followed in correct order")
	t8 = LabeledImage()
	cur_work_dir = os.getcwd()
	img_loc = cur_work_dir + "/test_images/" + "t1_image.jpg"
	# print(current_path)
	t8.loadImage(img_loc)
	t8.addRule("u:testuser1", ("POLYLINE", [(100, 100), (300, 100), (200, 300)]), "ALLOW")
	t8.addRule("u:testuser1", ("POLYLINE", [(200, 100), (100, 300), (300, 300)]), "BLUR")
	# t8.addRule("u:testuser1", ("POLYLINE", [(100, 100), (100, 300), (300, 300),(300,100)]), "DENY")
	if t8.rule_list[0]["action"] == "ALLOW" and t8.rule_list[1]["action"] == "BLUR":
		print("Rule Addition works correctly")
	else:
		print("Rule Addition fails. Here is how they are listed")
		for rule in t8.rule_list:
			print(rule)


def Test16():  # DEFAULT DENY - ALLOW A PORTION EDGE CASE
	print()
	print("Test 16 multiple rules default action Deny")
	t8 = LabeledImage()
	cur_work_dir = os.getcwd()
	img_loc = cur_work_dir + "/test_images/" + "t1_image.jpg"
	# print(current_path)
	t8.loadImage(img_loc)
	t8.setDefault("DENY")
	t8.addRule("u:testuser1", ("POLYLINE", [(100, 100), (300, 100), (200, 300)]), "ALLOW")
	t8.addRule("u:testuser1", ("POLYLINE", [(200, 100), (100, 300), (300, 300)]), "DENY")
	for rule in t8.rule_list:
		print(rule)
	t8.getImage("testuser1")


def Test17():
	print()
	print("Test 17 multiple rules")
	t8 = LabeledImage()
	cur_work_dir = os.getcwd()
	img_loc = cur_work_dir + "/test_images/" + "t1_image.jpg"
	# print(current_path)
	t8.loadImage(img_loc)
	t8.addRule("u:testuser1", ("POLYLINE", [(100, 100), (300, 100), (200, 300)]), "ALLOW")
	# t8.addRule("u:testuser1", ("POLYLINE", [(200, 100), (100, 300), (300, 300)]), "DENY")
	t8.addRule("u:testuser1", ("POLYLINE", [(100, 100), (100, 300), (300, 300), (300, 100)]), "DENY")
	for rule in t8.rule_list:
		print(rule)
	t8.getImage("testuser1")


def Test18():
	print()
	print("Test 18 multiple rules")
	t8 = LabeledImage()
	cur_work_dir = os.getcwd()
	img_loc = cur_work_dir + "/test_images/" + "t1_image.jpg"
	# print(current_path)
	t8.loadImage(img_loc)
	t8.addRule("u:testuser1", ("CIRCLE", 200, 200, 100), "ALLOW")
	t8.addRule("u:testuser1", ("CIRCLE", 200, 200, 150), "DENY")
	t8.addRule("u:testuser1", ("CIRCLE", 200, 200, 200), "BLUR")
	for rule in t8.rule_list:
		print(rule)
	t8.getImage("testuser1")

def Test19():
	print()
	print("Test 19 multiple rules and with Regex")
	t8 = LabeledImage()
	cur_work_dir = os.getcwd()
	img_loc = cur_work_dir + "/test_images/" + "t1_image.jpg"
	# print(current_path)
	t8.loadImage(img_loc)
	t8.addRule("m:^test", ("CIRCLE", 200, 200, 100), "ALLOW")
	t8.addRule("m:^test", ("CIRCLE", 200, 200, 150), "DENY")
	t8.addRule("m:^test", ("CIRCLE", 200, 200, 200), "BLUR")
	for rule in t8.rule_list:
		print(rule)
	t8.getImage("testuser1")

def Test20():
	Database.dbclient.drop_database("img_tool_db")
	print()
	print("Test 20 multiple rules and with groupname & username")
	print("user1 DENY cycle and inside of CIRCLE ALLOW , user2 BLUR CIRCLE")
	U = UserGroup()
	U.addGroup("group1")
	U.addUser("user1",["group1"],"pass1")
	U.addUser("user2",[],"pass2")

	t8 = LabeledImage()
	cur_work_dir = os.getcwd()
	img_loc = cur_work_dir + "/test_images/" + "t1_image.jpg"
	# print(current_path)
	t8.loadImage(img_loc)
	t8.addRule("u:user1", ("CIRCLE", 200, 200, 100), "ALLOW")
	t8.addRule("g:group1", ("CIRCLE", 200, 200, 150), "DENY")
	t8.addRule("u:user2", ("CIRCLE", 200, 200, 200), "BLUR")
	for rule in t8.rule_list:
		print(rule)
	t8.getImage("user1")
	t8.getImage("user2")
