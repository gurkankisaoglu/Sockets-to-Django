import cv2
import pickle
from bson.binary import Binary
from Database import Database
from models import Image
import pymongo
import numpy as np
import userGroup

class LabeledImage():
	#static members

	def __init__(self, owner=""):
		self.owner = owner
		self.name=""
		self.db = Database.dbclient
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
		#TODO In case of failure it returns an empty image, check this out
		#it will use cv2.imdecode (for buffer)


	def loadImage(self,filepath):
		#as we gathered this is used when image is already at disk
		# sets image content from a absolute file path
		self.img = cv2.imread(filepath)
		self.img_initialized = True

			#it will use cv2.imread

	def setDefault(self, action):
		self.default_action=action

	# TODO : make an addition to add current file path

	def load(self,name):
		query = {"name":name}
		result = self.db["img_tool_db"]["imageDB"].find_one(query)

		self.img = pickle.loads(result["img"])
		self.rule_list = result["rule_list"]
		self.img_initialized = result["is_initialized"]
		self.default_action = result["defaultAction"]

	def save(self,name):
		self.name = name
		self.db["img_tool_db"]["imageDB"].create_index([("name",pymongo.ASCENDING)],unique=True)
		temp = Binary(pickle.dumps(self.img,protocol=2))
		image_class = Image.Image(self.owner,name,temp,self.img_initialized,self.rule_list,self.default_action)
		self.db["img_tool_db"]["imageDB"].insert_one(image_class.__dict__)


	def delRule(self,pos):
		if(self.rule_list.size()<=pos):
				print("Rule Not Found")
		else:
			del self.rule_list[pos]

	def addRule(self,matchexpr,shape,action,pos=-1):
		rule = {}
		if(matchexpr[0]=="u"):
			rule["type"] = "user"
		elif (matchexpr[0] == "g"):
			rule["type"] = "group"
		else:
			rule["type"] = "regex"

		rule["effects"] = matchexpr[2:]
		rule["shape"] = shape
		rule["action"] = action
		if(pos == -1):
			self.rule_list.append(rule)
		else:
			self.rule_list.insert(pos , rule)
		self.db["img_tool_db"]["imageDB"].find({"name": self.name})
		self.db["img_tool_db"]["imageDB"].update_one({"name": self.name}, {"$set": {
			"rule_list": self.rule_list
		}}, upsert= True)


	def getImage(self,user):

		userGroupLink = userGroup.UserGroup()
		kernel = np.ones((7, 7), np.float32) / 49
		temp_img = None
		# this part is the default part
		if self.default_action == "DENY":
			temp_img = np.copy(self.img)
			temp_img[:, :] = 0
		elif self.default_action == "BLUR":
			temp_img = cv2.filter2D(self.img, -1, kernel)
		else:
			temp_img = np.copy(self.img) #almost blew up the code
		if self.rule_list:
			for rule in reversed(self.rule_list):
				rule_applies = False
				if rule["type"]=="user" and user == rule["effects"]:
					rule_applies=True
				elif rule["type"]=="group" and userGroupLink.ismember(user,rule["effects"]):
					rule_applies=True
				elif rule["type"]=="regex":
					regex = rule["effects"] # TODO as far as i gather if regexsearch has this user in its results we use it
					if userGroupLink.regexsearch(user,regex):
						rule_applies=True

				if rule_applies:
					if rule["shape"][0]=="RECTANGLE":
						x1=rule["shape"][1]
						y1=rule["shape"][2]
						x2=rule["shape"][3]
						y2=rule["shape"][4]# type of shape is first element of tuple(which is str)

						if rule["action"] == "ALLOW":
							temp_img[y1:y2 , x1:x2] = self.img[y1:y2,x1:x2]
						elif rule["action"] == "DENY":
							temp_img[y1:y2 , x1:x2] = 0
						elif rule["action"] == "BLUR":
							cropped_part = self.img[y1:y2,x1:x2]
							temp_img[y1:y2,x1:x2] = cv2.filter2D(cropped_part, -1, kernel)


						else:
							raise ValueError # action cannot be anything else
					elif rule["shape"][0]=="CIRCLE":
						x = rule["shape"][1]
						y = rule["shape"][2]
						r = rule["shape"][3]

						if rule["action"] == "ALLOW":
							black_mask = np.zeros(self.img.shape, dtype="uint8") # gives us the image we need allowed
							cv2.circle(black_mask, (x, y), r, (255, 255, 255), -1)
							cv2.bitwise_and(self.img, black_mask, black_mask)

							white_mask = np.copy(temp_img) # need copy? just on top of temp image?
							cv2.circle(white_mask, (x, y), r, (0, 0, 0), -1)

							cv2.add(white_mask, black_mask, temp_img)
						elif rule["action"] == "DENY":
							mask = np.ones(self.img.shape, dtype="uint8")*255
							cv2.circle(mask,(x,y),r,(0,0,0),-1)
							cv2.bitwise_and(temp_img,mask,temp_img)
						elif rule["action"] == "BLUR": #TODO improve performance
							white_mask = np.copy(temp_img)
							cv2.circle(white_mask, (x, y), r, (0, 0, 0), -1) # this gives us an image with black circle

							black_mask = np.zeros(self.img.shape, dtype="uint8")
							cv2.circle(black_mask, (x, y), r, (255, 255, 255), -1) # this gives us a black mask with white circle

							blur_mask = np.copy(temp_img)
							cv2.filter2D(blur_mask, -1, kernel, blur_mask)
							cv2.bitwise_and(blur_mask, black_mask, black_mask)

							cv2.add(white_mask,black_mask,temp_img)
						else:
							raise ValueError  # action cannot be anything else

					elif rule["shape"][0] == "POLYLINE":
						vertices = np.asarray(rule["shape"][1])
						if rule["action"] == "ALLOW":
							black_mask = np.zeros(self.img.shape, dtype="uint8") # gives us the image we need allowed
							cv2.fillConvexPoly(black_mask, vertices, (255, 255, 255))
							cv2.bitwise_and(self.img, black_mask, black_mask)

							white_mask = np.copy(temp_img)
							cv2.fillConvexPoly(white_mask, vertices, (0, 0, 0))

							cv2.add(white_mask, black_mask, temp_img)

						elif rule["action"] == "DENY":
							mask = np.ones(self.img.shape, dtype="uint8")*255
							cv2.fillConvexPoly(temp_img,vertices,(0,0,0))
							cv2.bitwise_and(temp_img,mask,temp_img)

						elif rule["action"] == "BLUR": #TODO improve performance
							white_mask = np.copy(temp_img)
							cv2.fillConvexPoly(white_mask, vertices, (0, 0, 0)) # this gives us an image with black circle

							black_mask = np.zeros(self.img.shape, dtype="uint8")
							cv2.fillConvexPoly(black_mask, vertices, (255, 255, 255)) # this gives us a black mask with white circle

							blur_mask = np.copy(temp_img)
							cv2.filter2D(blur_mask, -1, kernel, blur_mask)
							cv2.bitwise_and(blur_mask, black_mask, black_mask)

							cv2.add(white_mask,black_mask,temp_img)
						else:
							raise ValueError  # action cannot be anything else

					else:
						raise ValueError # if this happens shape is given incorrectly
		#TODO delete this part
		"""cv2.imshow(user +' final image', temp_img)
		k = cv2.waitKey(0) & 0xFF  # 64 bit requires this
		cv2.destroyAllWindows()"""
		return temp_img

	#functions added for debugging purposes
	def showImage(self):
		if(self.img_initialized):

			cv2.imshow('image', self.img)
			k = cv2.waitKey(0) & 0xFF # 64 bit requires this
			cv2.destroyAllWindows()

	#TODO this doesnt work
	def list_all_images(self):
		results = self.db["img_tool_db"]["imageDB"].find()
		for image in results:
			print(image)

	def retrieve_image(self):
		return self.img

	def setOwner(self,new_owner):
		self.owner = new_owner