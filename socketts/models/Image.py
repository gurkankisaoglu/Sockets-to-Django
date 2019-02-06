from mongoengine import *


class Image(Document):

	def __init__(self, owner , name , img , is_initialized=False , rule_list = [] , defaultAction = "ALLOW" , *args, **kwargs):
		super(Document, self).__init__(*args, **kwargs)
		self.owner = owner
		self.name = name
		self.img = img
		self.is_initialized = is_initialized
		self.rule_list = rule_list
		self.defaultAction = defaultAction


