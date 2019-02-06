import socket
import userGroup
import labeledImage
import pickle
import threading
from threading import Lock,RLock,Condition,Thread
from models import User
import os , sys
import cv2
from networking import socketdriver
import time

def checkfree(s):
    try:
        r = s.index('FREE')
        return r
    except: # No free socket found
        return None


class Server:
	def __init__(self,port=12345,simultaneous_connections=5):

		self.port = port
		self.server_sock = None
		self.userGroupLink = None
		self.simultaneous_connections = simultaneous_connections
		self.host = ""
		self.max_size = 1024
		self.isInitialized = False
		self.number_of_working_threads = 5
		self.tLock = Lock()
		self.free_socket_list=None
		self.readyCondition = Condition(self.tLock)
		self.conditions = None
		self.serving_threads = None
		self.terminate_flag = False
		#self.timeout = 500

	def initialize(self):

		try:
			self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			print("Server Socket successfully created")
		except socket.error:
			print("Server Socket Cannot Be Created,kill the process occupying the port 12345.")
			os.system("lsof -PiTCP | grep 12345")
			sys.exit(-1)

		# TODO START INITIALIZATIONS EACH THREAD STARTS WITH A CLEAN IMAGE

		self.free_socket_list = ['FREE'] * self.number_of_working_threads
		self.conditions = [Condition(self.tLock) for i in range(self.number_of_working_threads)]
		self.userGroupLink = userGroup.UserGroup()

		# TODO DELETE THIS LINE ITS FOR DEBUGGING PURPOSES
		self.userGroupLink.clear_database()
		self.userGroupLink.addUser("admin", [], "admin")

		self.serving_threads = [Thread (target = self._run_and_serve, args=(self.free_socket_list, thread_id, self.conditions[thread_id], self.readyCondition,None,)) for thread_id in range(self.number_of_working_threads)]


		# TODO END INITIALIZATIONS
		self.server_sock.bind(('', self.port))
		#self.server_sock.settimeout(self.timeout)
		print("Server is listening on port {}".format(self.port))

		self.server_sock.listen(self.simultaneous_connections)
		self.isInitialized = True
		print("Server is initialized and will accept connections")
		print("Connection will timeout in 60 seconds if no interaction occurs.")
		print()

		for server in self.serving_threads:
			server.start()

		try:
			while True:
				#print("Before loop"+str(self.i))
				client, address = self.server_sock.accept()
				print("Connection came from : ",address)
				#print("After accept" + str(self.i))

				#TODO ADDED DEBUG
				with self.tLock:
					r = checkfree(self.free_socket_list)
					while r == None:
						self.readyCondition.wait()
						r = checkfree(self.free_socket_list)
					print("Found free socket")
					self.free_socket_list[r] = client # you change the "FREE" to a socket item so thread can pick it up
					self.conditions[r].notify()

				# TODO ADDED DEBUG

		except Exception as e: #TIMEOUT
			print("exitting", str(e), ". Will wait for ongoing connections to close")
			self.terminate_flag = True #SERVER IS CLOSING SHUT THREADS DOWN

		for i in range(self.number_of_working_threads):  # let all workers terminate
			with self.tLock:
				self.conditions[i].notify()

		#TODO THREADS ARE GETTING SHUTDOWN BUT TIMEOUT IN THREAD DOESN'T MAKE IT CLOSE
		for server in self.serving_threads:
			server.join()

		self.server_sock.close()



	def _run_and_serve(self, sockets, myid, mycond, done, thread_image):
		print("Server Thread {} started".format(myid))
		if not self.isInitialized:
			raise Exception("Cannot Run an Uninitialized Server, use Server.initialize() method.")

		#TODO DEBUG ADDED START

		while not self.terminate_flag:
			with mycond:
				while not self.terminate_flag and type(sockets[myid]) == str: #in the beginning all threads wait here, each one on their conditions
					#print("DEBUG // Thread {} Waiting for condition.".format(myid))
					mycond.wait()
					#print("DEBUG // Thread {} No longer Waits for condition.".format(myid))
				if self.terminate_flag:
					print("Terminate signal came .".format(myid))
					break
				print("with mycond part")
			print("DEBUG" , myid , "serving", sockets[myid].getpeername())

			thread_image = labeledImage.LabeledImage()

			connection = sockets[myid]

			operation = connection.recv(self.max_size).decode("ascii")
			#print("DEBUG // Operation : " + operation)
			if operation == "login" :
				print("Server received a login request.")
				received_username = connection.recv(self.max_size).decode("ascii")
				print("DEBUG // Received username is : " + received_username)
				received_password = connection.recv(self.max_size).decode("ascii")
				print("DEBUG // Received password is : " + received_password)
				accountFound = self.userGroupLink.checkLogin(received_username, received_password)

				connection.send(accountFound.encode("ascii"))  # Send the response to client
				time.sleep(0.1)

				if accountFound == "True":  # Login is successful
					while True:
						# TODO WHEN YOU LOGGED IN HERE AND DO NOTHING AND GET TIME OUT THIS FUCKS UP
						operation = connection.recv(self.max_size).decode("ascii")
						print("Operation Received : "+operation)

						if operation == "addGroup":
							self._addGroupHandler(connection)

						elif operation == "addUser":
							self._addUserHandler(connection)

						elif operation == "delGroup":
							self._delGroupHandler(connection)

						elif operation == "delUser":
							self._delUserHandler(connection)

						elif operation == "getGroups":
							self._getGroupsHandler(connection)

						elif operation == "getUsers":
							self._getUsersHandler(connection)

						elif operation == "setPassword":
							self._setPasswordHandler(connection)

						elif operation == "isMember":
							self._isMemberHandler(connection)
						#TODO operations involving images require you to pass thread image as parameter for seperation for each thread
						elif operation == "setImage":
							self._setImageHandler(connection,thread_image)

						elif operation == "loadImage":
							self._loadImageHandler(connection,thread_image)

						elif operation == "setDefault":
							self._setDefaultHandler(connection,thread_image)

						elif operation == "save":
							self._saveHandler(connection,thread_image,received_username)

						elif operation == "load":
							self._loadHandler(connection,thread_image,received_username)

						elif operation == "imageList":
							self._imageListHandler(connection)

						elif operation == "addRule":
							self._addRuleHandler(connection,thread_image,received_username)

						elif operation == "delRule":
							self._delRuleHandler(connection,thread_image,received_username)

						elif operation == "getImage":
							self._getImageHandler(connection,thread_image,received_username)

						elif operation == "closeConnection":
							print("Connection with client is closed.")
							break
						else:
							print("Undefined or Erroneous Operation. Exiting!")
							break

				else:
					print("Account is not found, connection will be terminated.")
			else:
				print("Server didn't receive any operation data.")

			print(sockets[myid].getpeername(), ' closing')
			sockets[myid].close()
			with mycond:
				sockets[myid] = 'FREE'
				done.notify()
		if type(sockets[myid]) == socket:
			sockets[myid].close()

		# TODO DEBUG ADDED END


	def _addGroupHandler(self,connection):
		groupname = connection.recv(self.max_size).decode("ascii")
		self.userGroupLink.addGroup(groupname)

	def _addUserHandler(self,connection):
		inp = connection.recv(self.max_size).decode("ascii")
		username = inp.split(" ")[0]
		password = inp.split(" ")[1]
		groups = connection.recv(self.max_size).decode("ascii").split(" ")
		self.userGroupLink.addUser(username, groups, password)

	def _delGroupHandler(self,connection):
		groupname = connection.recv(self.max_size).decode("ascii")
		self.userGroupLink.delGroup(groupname)

	def _delUserHandler(self, connection):
		username = connection.recv(self.max_size).decode("ascii")
		self.userGroupLink.delUser(username)

	def _getGroupsHandler(self,connection):
		username = connection.recv(self.max_size).decode("ascii")
		list = self.userGroupLink.getGroups(username)
		if list:
			list = "-".join(list)
			connection.send(list.encode("ascii"))
			time.sleep(0.1)
		else:
			connection.send(b'None')
			time.sleep(0.1)


	def _getUsersHandler(self, connection):
		groupname = connection.recv(self.max_size).decode("ascii")
		list = self.userGroupLink.getUsers(groupname)
		if len(list) != 0:
			list = "-".join(list)
			connection.send(list.encode("ascii"))
			time.sleep(0.1)
		else:
			connection.send(b'None')
			time.sleep(0.1)

	def _setPasswordHandler(self, connection):
		inp = connection.recv(self.max_size).decode("ascii")
		self.userGroupLink.setPassword(inp.split(" ")[0], inp.split(" ")[1])


	def _isMemberHandler(self, connection):
		inp = connection.recv(self.max_size).decode("ascii")
		print(inp.split(" ")[0])
		print(inp.split(" ")[1])
		res = self.userGroupLink.ismember(inp.split(" ")[0], inp.split(" ")[1])
		if res:
			connection.send("True".encode("ascii"))
			time.sleep(0.1)
		else:
			connection.send("False".encode("ascii"))
			time.sleep(0.1)

	def _loadImageHandler(self, connection,thread_image):

		received_image = socketdriver.recv_msg(connection)
		thread_image.img = pickle.loads(received_image)
		if thread_image.img is not None:
			print("Correctly loads image")
			connection.send("Correctly Loaded Image".encode("ascii"))
		else:
			print("Didn't Load Image")
			connection.send("LoadImage Failed".encode("ascii"))
		time.sleep(0.1)

	def _setImageHandler(self, connection,thread_image):

		received_image = socketdriver.recv_msg(connection)
		thread_image.img = pickle.loads(received_image)
		if thread_image.img is not None:
			print("Correctly sets image")
			connection.send("Correctly Sets Image".encode("ascii"))
		else:
			print("Didn't Set Image")
			connection.send("Set Image Failed".encode("ascii"))
		time.sleep(0.1)

	def _setDefaultHandler(self, connection,thread_image):
		inp = connection.recv(self.max_size).decode("ascii")
		thread_image.setDefault(inp)
		time.sleep(0.1)

	def _saveHandler(self, connection,thread_image,new_owner):
		image_name = connection.recv(self.max_size).decode("ascii")
		thread_image.setOwner(new_owner)
		try:
			thread_image.save(image_name)
			print("Correctly saved image.")
			connection.send("Save Successful".encode("ascii"))
		except :
			print("Failed save.")
			connection.send("Save Failed".encode("ascii"))
		time.sleep(0.1)

	def _loadHandler(self, connection,thread_image,new_owner):
		image_name = connection.recv(self.max_size).decode("ascii")
		if self.userGroupLink.ownsImage(new_owner,image_name):
			try:
				thread_image.load(image_name)
				print("Correctly loads image.")
				connection.send("Load Successful".encode("ascii"))
			except:
				print("Failed load.")
				connection.send("Load Failed".encode("ascii"))
		else:
			print("Load Failed,Ownership requirement doesn't match.")
			connection.send("Load Failed,Ownership requirement doesn't match.".encode("ascii"))
		time.sleep(0.1)

	def _imageListHandler(self, connection):
		result = self.userGroupLink.getImageList()
		result_length = len(result)
		connection.send(str(result_length).encode("ascii"))
		time.sleep(0.1)
		for couple in result:
			send_string = couple[0] + " " + couple[1]
			connection.send(send_string.encode("ascii"))
			time.sleep(0.1)
		connection.send("End of ImageList.".encode("ascii"))
		time.sleep(0.1)
		print("Sent End Of List.")

	def _addRuleHandler(self,connection,thread_image,new_owner):
		#TODO it requires that image is saved to db atleast once
		given_rule = connection.recv(self.max_size).decode("ascii")
		if self.userGroupLink.ownsImage(new_owner,thread_image.name):
			try:
				thread_image.addRule()
				print("Correctly adds rule.")
				connection.send("Add Rule Successful".encode("ascii"))
			except:
				print("Failed Add Rule.")
				connection.send("Add Rule Failed".encode("ascii"))
		else:
			print("Add Rule Fails, Ownership requirement doesn't match.")
			connection.send("Add Rule Fails,Ownership requirement doesn't match.".encode("ascii"))
		time.sleep(0.1)

	def _delRuleHandler(self,connection,thread_image,new_owner):
		#TODO it requires that image is saved to db atleast once
		rule_position = connection.recv(self.max_size).decode("ascii")
		if self.userGroupLink.ownsImage(new_owner,thread_image.name):
			try:
				thread_image.delRule(rule_position)
				print("Correctly deletes rule.")
				connection.send("Del Rule Successful".encode("ascii"))
			except:
				print("Failed Del Rule.")
				connection.send("Del Rule Failed".encode("ascii"))
		else:
			print("Del Rule Fails, Ownership requirement doesn't match.")
			connection.send("Del Rule Fails,Ownership requirement doesn't match.".encode("ascii"))
		time.sleep(0.1)

	def _getImageHandler(self,connection,thread_image,current_user):
		#TODO it requires that image is saved to db atleast once
		temp_img = thread_image.getImage(current_user)
		temp_pickled = pickle.dumps(temp_img,protocol=2)
		socketdriver.send_msg(connection, temp_pickled)
		time.sleep(0.1)
		print("GetImage Completed")
		connection.send("Get Image Complete.".encode("ascii"))
		time.sleep(0.1)

