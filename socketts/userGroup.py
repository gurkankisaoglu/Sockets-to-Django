from Database import Database
from models import User
from models import Group
import pymongo


class UserGroup():
	"""uses mongodb for backend operations
	 class is an interface for user-group interactions"""
	#TODO Make this singleton so you dont have to create a redundant instance each time you call it
	#TODO make sure that an admin user with admin password is created before usage

	def __init__(self):
		self.db = Database.dbclient
		pass

	def addUser(self, name, groups, password):
		# add user to db
		self.db["img_tool_db"]["users"].create_index([("username", pymongo.ASCENDING)], unique=True)
		user = User.User(name, groups, password)
		self.db["img_tool_db"]["users"].insert_one(user.__dict__)

		for group in groups:
			DBGroup = self.db["img_tool_db"]["groups"].find_one({"groupname": group})
			if DBGroup:
				DBGroup["users_in_list"] += [name]
				self.db["img_tool_db"]["groups"].update_one({"groupname": group},
															{"$set": {"users_in_list": DBGroup["users_in_list"]}},
															upsert=True)
			else:
				newGroup = Group.Group(group, [name])
				self.db["img_tool_db"]["groups"].insert_one(newGroup.__dict__)

	def addGroup(self, name):
		# add group to db
		self.db["img_tool_db"]["groups"].create_index([("groupname", pymongo.ASCENDING)], unique=True)
		group = Group.Group(name, [])
		self.db["img_tool_db"]["groups"].insert_one(group.__dict__)

	def delUser(self, name):
		# del user from db
		del_query = {"username": name}
		groupsOfUser = self.db["img_tool_db"]["users"].find_one(del_query)["groups"]
		self.db["img_tool_db"]["users"].delete_one(del_query)
		for group in groupsOfUser:
			DBGroup = self.db["img_tool_db"]["groups"].find_one({"groupname": group})
			if DBGroup:
				DBGroup["users_in_list"].remove(name)
				self.db["img_tool_db"]["groups"].update_one({"groupname": group},
															{"$set": {"users_in_list": DBGroup["users_in_list"]}},
															upsert=True)

	def delGroup(self, groupname):
		users = self.db["img_tool_db"]["users"].find()
		group_del_query = {"groupname": groupname}
		for user in users:
			if groupname in user["groups"]:
				user["groups"].remove(groupname)
				self.db["img_tool_db"]["users"].update_one({"username": user["username"]},
														   {"$set": {"groups": user["groups"]}}, upsert=True)

		self.db["img_tool_db"]["groups"].delete_many(group_del_query)

	def getGroups(self, name):
		# get groups which user belongs to
		query = {"username": name}
		results = self.db["img_tool_db"]["users"].find_one(query)
		if results:
			return results["groups"]
		return None

	def getUsers(self, group):
		# get users which group have
		results = []
		users_list = self.db["img_tool_db"]["users"].find()
		for user in users_list:
			if group in user["groups"]:
				results.append(user["username"])
		return results

	def setPassword(self, user, password):
		# set user password
		query = {"username": user}
		new_values = {"$set": {"password": password}}
		self.db["img_tool_db"]["users"].update_one(query, new_values)

	def ismember(self, user, group):
		# is member of a group
		query = {"username": user, "groups": group}
		result = self.db["img_tool_db"]["users"].find_one(query)
		if not result:
			return False
		return True

	def regexsearch(self, user, regex):
		# if user exists in result of regexsearch return true
		query = {"username": {"$regex": regex}}  # find people who satisfy this regex
		result = self.db["img_tool_db"]["users"].find(query)
		if not result:
			return False
		return True

	def checkLogin(self, username, password):
		query = {"username": username, "password": password}
		print(query)
		result = self.db["img_tool_db"]["users"].find(query)
		if result.count() != 0:
			return "True"
		return "False"

	"""These are helper functions that help debugging process"""

	def list_all_users(self):
		results = self.db["img_tool_db"]["users"].find()
		for user in results:
			print(user)

	def list_all_groups(self):
		results = self.db["img_tool_db"]["groups"].find()
		for group in results:
			print(group)

	def delete_all_users(self):
		deleted_counter = self.db["img_tool_db"]["users"].delete_many({})
		print(deleted_counter.deleted_count, " users deleted.")

	def delete_all_groups(self):
		deleted_counter = self.db["img_tool_db"]["groups"].delete_many({})
		print(deleted_counter.deleted_count, "groups deleted.")

	def delete_all_images(self):
		deleted_counter = self.db["img_tool_db"]["imageDB"].delete_many({})
		print(deleted_counter.deleted_count, "images deleted.")

	def clear_database(self):
		print()
		self.delete_all_groups()
		self.delete_all_users()
		self.delete_all_images()
		print("Database is clear.")
		print()

	#TODO check if query is correct
	def ownsImage(self, username,imagename):
		query = {"owner": username, "name": imagename}
		result = self.db["img_tool_db"]["imageDB"].find_one(query)
		if not result:
			return False
		return True

	def getImageList(self):  # returns list of tuples
		results = []
		image_list = self.db["img_tool_db"]["imageDB"].find()
		for image in image_list:
			print(image)
			results.append((image["owner"], image["name"]))
		return results
