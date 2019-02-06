import cv2
import pickle
from bson.binary import Binary
import numpy as np

class LabeledImage():
	#static members

	def __init__(self, owner=""):
		self.owner = owner
		self.name=""
		#We require a rule list for each LayeredImage to know what to do with each user
		self.rule_list=[]
		self.img_initialized=False
		#implementation of default action can be improved by enumeration or mapping them to a special function
		self.img=None
		self.default_action = "ALLOW"

	def setImage(self,buffer):
		#most likely this part will be used incase image is taken from internet
		#sets image content from a binary buffer
		#image type can be jpeg or png

		#TODO : IT ASSUMES THAT IMAGE IS COLORED IF ITS NOT IT WILL EXPLODE


		self.img = cv2.imdecode(buffer[1],cv2.IMREAD_COLOR)
		self.img_initialized = True


