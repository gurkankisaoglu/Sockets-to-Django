from mongoengine import *


class Group(Document):

	def __init__(self, groupname=None, users_in_list=[], *args, **kwargs):
		super(Document, self).__init__(*args, **kwargs)
		self.groupname = groupname
		self.users_in_list = users_in_list