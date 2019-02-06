import socket
import getpass
import pickle
import labeledImage
import userGroup
import time
import sys
import cv2


#TODO this can be made into a whole class
from networking import socketdriver


class Client:
	def __init__(self,port = 12345):
		self.username = ""
		self.password = ""
		self.port = port
		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		except socket.error:
			print("Client Socket Cannot Be Created")
			sys.exit(-1)
		#TODO NOT SURE ABOUT THIS may be removed
		#self.sock.settimeout(500)
		self.userGroupLink = None
		self.image = None


	def connect(self): #TODO DOESN'T FUCKING WORK WITHOUT time.sleep ???
		self.sock.connect(('127.0.0.1', self.port))
		print("Input Username : ")
		#TODO uncomment
		self.username = input()
		self.password = getpass.getpass()
		try:
			self.sock.send("login".encode("ascii"))
			time.sleep(0.1)
		except TimeoutError:
			print("DEBUG// LOGIN-NO RESPONSE FROM SERVER")
			sys.exit(-1)
		self.sock.send(self.username.encode("ascii"))
		time.sleep(0.1)
		self.sock.send(self.password.encode("ascii"))
		time.sleep(0.1)

		self.image = labeledImage.LabeledImage()
		self.userGroupLink = userGroup.UserGroup()
		#TODO send username and password as a tuple?
		self.operations()

	def operations(self):
		server_response = self.sock.recv(1024).decode("ascii")
		time.sleep(0.1)
		#print("DEBUG// Server response is "+ server_response)
		if server_response == "True":
			print("Login Successful")
			self.image = labeledImage.LabeledImage()
			while True:
				if self.username == "admin":
					print()
					print("Admin Operations")
					print("<----------------->")
					print("1) Add Group ")
					print("2) Add User ")
					print("3) Del Group ")
					print("4) Del User ")
					print("5) Get Groups of a User ")
					print("6) Get Users of a group ")
					print("7) Set Password ")
					print("8) Is Member ")
					print("9) Exit ")
				else:
					print()
					print("User Operations")
					print("<----------------->")
					print("1) Get groups of a user ")
					print("2) Get users of a group ")
					print("3) Set password ")
					print("4) Is member ")
					print("5) Exit ")

				#Common Operations TODO these all require that an image is loaded
				print("(11) setImage from buffer ")
				print("(12) loadImage from filepath ")
				print("(13) setDefault action of image ")
				print("(14) load image from DB ")
				print("(15) save image to DB ")
				print("(16) addRule ")
				print("(17) delRule ")
				print("(18) getImage ")
				print("(19) imageList ")

				operation = input()

				if (operation == "9") or (self.username != "admin" and operation == "5"):
					print("Client Succesfully Exited")
					self.sock.send("closeConnection".encode("ascii"))
					time.sleep(0.1)
					break

				elif self.username == "admin" and operation == "1":
					self.addGroupRequest()

				elif self.username == "admin" and operation == "2":
					self.addUserRequest()

				elif self.username == "admin" and operation == "3":
					self.delGroupRequest()

				elif self.username == "admin" and operation == "4":
					self.delUserRequest()

				elif (self.username == "admin" and operation == "5") or (self.username != "admin" and operation == "1"):
					self.getGroupsRequest()

				elif (self.username == "admin" and operation == "6") or (self.username != "admin" and operation == "2"):
					self.getUserRequest()

				elif (self.username == "admin" and operation == "7") or (self.username != "admin" and operation == "3"):
					self.setPasswordRequest()

				elif (self.username == "admin" and operation == "8") or (self.username != "admin" and operation == "4"):
					self.isMemberRequest()

				elif operation == "11":
					self.setImageRequest()

				elif operation == "12":
					self.loadImageRequest()

				elif operation == "13":
					self.setDefaultRequest()

				elif operation == "14":
					self.loadRequest()

				elif operation == "15":
					self.saveRequest()

				elif operation == "16":
					self.addRuleRequest()

				elif operation == "17":
					self.delRuleRequest()

				elif operation == "18":
					self.getImageRequest()

				elif operation == "19":
					self.imageListRequest()

				else:
					print("Undefined Action, exiting.")
					self.sock.close()
					break
		else:
			print("Cannot login, connection will be closed")
		self.sock.close()

	def addGroupRequest(self):
		self.sock.send("addGroup".encode("ascii"))
		time.sleep(0.1)
		print("enter groupname:")
		groupname = input()
		self.sock.send(groupname.encode("ascii"))
		time.sleep(0.1)
		print()
		print("Press a key to continue...")
		input()

	def addUserRequest(self):
		self.sock.send("addUser".encode("ascii"))
		time.sleep(0.1)
		print("Enter Username and Password Respectively:")
		inp = input()
		print("Enter which groups user belongs to:")
		groups = input()
		self.sock.send(inp.encode("ascii"))
		time.sleep(0.1)
		self.sock.send(groups.encode("ascii"))
		time.sleep(0.1)
		print()
		print("Press a key to continue...")
		input()

	def delGroupRequest(self):
		self.sock.send("delGroup".encode("ascii"))
		time.sleep(0.1)
		print("Enter groupname you want to delete")
		groupname = input()
		self.sock.send(groupname.encode("ascii"))
		time.sleep(0.1)
		print()
		print("Press a key to continue...")
		input()

	def delUserRequest(self):
		self.sock.send("delUser".encode("ascii"))
		time.sleep(0.1)
		print("enter username you want to delete")
		userToDelete = input()
		self.sock.send(userToDelete.encode("ascii"))
		time.sleep(0.1)
		print()
		print("Press a key to continue...")
		input()

	def getGroupsRequest(self):
		self.sock.send("getGroups".encode("ascii"))
		time.sleep(0.1)
		print("enter self.username that you want to get groups")
		user = input()
		self.sock.send(user.encode("ascii"))
		time.sleep(0.1)
		result_list = self.sock.recv(1024).decode("ascii")
		print(result_list)
		print()
		print("Press a key to continue...")
		input()

	def getUserRequest(self):
		self.sock.send("getUsers".encode("ascii"))
		time.sleep(0.1)
		print("enter groupname that you want to get users")
		group = input()
		self.sock.send(group.encode("ascii"))
		time.sleep(0.1)
		result_list = self.sock.recv(1024).decode("ascii")
		print(result_list)
		print()
		print("Press a key to continue...")
		input()

	def setPasswordRequest(self):
		self.sock.send("setPassword".encode("ascii"))
		time.sleep(0.1)
		print("enter new password:")
		self.sock.send((self.username + " " + getpass.getpass()).encode("ascii"))
		time.sleep(0.1)
		#TODO maybe resend password data for checking if really recieved
		print()
		print("Press a key to continue...")
		input()

	def isMemberRequest(self):
		self.sock.send("isMember".encode("ascii"))
		time.sleep(0.1)
		print("self.username and groupname respectively(seperate with blank space)")
		self.sock.send((input()).encode("ascii"))
		time.sleep(0.1)
		res = self.sock.recv(1024).decode("ascii")
		print(res)
		print()
		print("Press a key to continue...")
		input()

	def loadImageRequest(self):
		self.sock.send("loadImage".encode("ascii"))
		time.sleep(0.1)
		print("Enter Full Filepath:")
		path = input()
		self.image.loadImage(path)
		sending_image = pickle.dumps(self.image.retrieve_image(),protocol=2)
		socketdriver.send_msg(self.sock,sending_image)
		time.sleep(0.1)
		result = self.sock.recv(1024).decode("ascii")
		print(result)
		print()
		print("Press a key to continue...")
		input()

	def setImageRequest(self):
		self.sock.send("setImage".encode("ascii"))
		time.sleep(0.1)
		print("Input the stream source:")
		# TODO DONT KNOW HOW TO INPUT ENCODED SOURCE? just accept it as a UNIX filepath
		encoded_source = input()
		self.image.setImage(encoded_source)
		sending_image = pickle.dumps(self.image.retrieve_image(),protocol=2)
		socketdriver.send_msg(self.sock,sending_image)
		time.sleep(0.1)
		result = self.sock.recv(1024).decode("ascii")
		print(result)
		print()
		print("Press a key to continue...")
		input()

	def setDefaultRequest(self):
		self.sock.send("setDefault".encode("ascii"))
		time.sleep(0.1)
		print("Enter New Default Action")
		self.sock.send((input()).encode("ascii"))
		time.sleep(0.1)
		print()
		print("Press a key to continue...")
		input()

	def saveRequest(self):
		self.sock.send("save".encode("ascii"))
		time.sleep(0.1)
		print("Enter name for saving image..")
		self.sock.send((input()).encode("ascii"))
		time.sleep(0.1)
		print("Saving Image...")
		result = self.sock.recv(1024).decode("ascii")
		print(result)
		print()
		print("Press a key to continue...")
		input()

	def loadRequest(self):
		self.sock.send("load".encode("ascii"))
		time.sleep(0.1)
		print("Enter name for loading image..")
		self.sock.send((input()).encode("ascii"))
		time.sleep(0.1)
		print("Loading Image...")
		result = self.sock.recv(1024).decode("ascii")
		print(result)
		print()
		print("Press a key to continue...")
		input()

	def imageListRequest(self):
		self.sock.send("imageList".encode("ascii"))
		time.sleep(0.1)
		print("Loading ImageList...")
		result_size = int(self.sock.recv(1024).decode("ascii"))
		while result_size>0:
			result = self.sock.recv(1024).decode("ascii")
			couple = result.split(" ")
			print("Owner : ", couple[0], " imagename : ", couple[1])
			result_size -= 1

		result = self.sock.recv(1024).decode("ascii")
		print(result)
		print()
		print("Press a key to continue...")
		input()
	def addRuleRequest(self):
		self.sock.send("addRule".encode("ascii"))
		time.sleep(0.1)
		print("Enter rule to add ...")
		self.sock.send((input()).encode("ascii"))
		time.sleep(0.1)
		print("Adding rule...")
		result = self.sock.recv(1024).decode("ascii")
		print(result)
		print()
		print("Press a key to continue...")
		input()

	def delRuleRequest(self):
		self.sock.send("delRule".encode("ascii"))
		time.sleep(0.1)
		print("Enter rule position to delete ...")
		self.sock.send((input()).encode("ascii"))
		time.sleep(0.1)
		print("Adding rule...")
		result = self.sock.recv(1024).decode("ascii")
		print(result)
		print()
		print("Press a key to continue...")
		input()

	def getImageRequest(self):
		self.sock.send("getImage".encode("ascii"))
		time.sleep(0.1)
		print("Getting Image for Given User")

		temp_pickled = socketdriver.recv_msg(self.sock)
		temp_img = pickle.loads(temp_pickled)

		cv2.imshow(self.username +' getImage Result', temp_img)
		k = cv2.waitKey(0) & 0xFF  # 64 bit requires this
		cv2.destroyAllWindows()

		result = self.sock.recv(1024).decode("ascii")
		print(result)
		print()
		print("Press a key to continue...")
		input()
