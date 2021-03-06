import RPi.GPIO as GPIO
from time import sleep

class sender(object):
	def __init__(self, data_pin=13, clock_pin=15, time_duration=0.005):
		self.clock_pin = clock_pin
		self.data_pin = data_pin
		self.timing_duration = time_duration
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(self.data_pin, GPIO.OUT)
		GPIO.setup(self.clock_pin, GPIO.OUT)
		
	def send_data(self, data, duration):
		GPIO.output(self.clock_pin, GPIO.HIGH)
		if data == "1":
			GPIO.output(self.data_pin, GPIO.HIGH)
		else:
			GPIO.output(self.data_pin, GPIO.LOW)
		sleep(duration)
		GPIO.output(self.clock_pin, GPIO.LOW)
		GPIO.output(self.data_pin, GPIO.LOW)
		sleep(duration)
		
	def send(self, eingabe=""):
		binary_list = []
		if eingabe == "":
			eingabe = (raw_input("Message: ") + "\n")
		for c in eingabe:
			c_binary = format(ord(c), "08b")
			binary_list.append(c_binary)
		print binary_list
		for element in binary_list:
			self.send_data("1", self.timing_duration)
			for bit in element:
				self.send_data(bit, self.timing_duration)
			GPIO.output(self.clock_pin, GPIO.LOW)
			sleep(self.timing_duration)
			
	def send_file(self, file_location):
		f = open(file_location, "r")
		file_content = f.read()
		file_length = len(file_content)
		print file_length
		print "Sending :[",
		for character in file_content:
			try:
				index = file_content.index(character)
				percentage = int((index / file_length) * 100)
				if percentage % 10:
					print "#",
			except ValueError:
				print "Error in indexing send object"
			self.send_data("1", self.timing_duration)
			c_binary = format(ord(character), "08b")
			#print c_binary
			for bit in c_binary:
				self.send_data(bit, self.timing_duration)
			GPIO.output(self.clock_pin, GPIO.LOW)
			sleep(self.timing_duration)
		print "]"
		print "Finished"
	
	def close_connection(self):
		GPIO.cleanup()

class empfaenger(object):
	def __init__(self, data_pin=16, clock_pin=18):
		'''Sets the Board up and configures the pins
		'''
		self.data_pin = data_pin
		self.clock_pin = clock_pin
		self.daten = []
		self.looked = False
		print("Setup...")
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(self.data_pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
		GPIO.setup(self.clock_pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

	def recieve(self, end_with_EOL = True):
		'''Is the main loop'''
		while True:
			recv_thing = [0,0]
			recv_thing = []
			while (len(recv_thing) <= 8):
				if GPIO.input(self.clock_pin) == True and GPIO.input(self.data_pin) == True and self.looked == False:
					recv_thing.append(1)
					self.looked = True
					#print "Recieved a 1"
				elif GPIO.input(self.clock_pin) == True and GPIO.input(self.data_pin) == False and self.looked == False:
					recv_thing.append(0)
					self.looked = True
					#print "Recieved a 0"
				elif GPIO.input(self.clock_pin) == False:
					self.looked = False
				sleep(0.000000001)
			self.daten.append(recv_thing[1:])
			#Break if EOL is recieved
			string_of_recv = str(recv_thing[1:])
			string_of_recv = string_of_recv.replace("[", '')
			string_of_recv = string_of_recv.replace("]", '')
			string_of_recv = string_of_recv.replace(",", '')
			string_of_recv = string_of_recv.replace(" ", '')
			#print string_of_recv
			recv_int = int(string_of_recv, 2)
			#print recv_int
			if recv_int == 10 and end_with_EOL == True:
				break

	def make_HR(self):
		satz = ""
		for recv_byte in self.daten:
			recv_string = str(recv_byte)
			recv_string = recv_string.replace("[", '')
			recv_string = recv_string.replace("]", '')
			recv_string = recv_string.replace(",", '')
			recv_string = recv_string.replace(" ", '')
			#print "String:" + str(recv_string)
			recv_int = int(recv_string, 2)
			#print "Integer:" + str(recv_int)
			buchstabe = chr(recv_int)
			#print "Character:" + str(buchstabe)
			satz += str(buchstabe)
			#print "Satz:" + str(satz)
		return satz
		
	def write_to_file(self, target_file):
		satz = ""
		for recv_byte in self.daten:
			recv_string = str(recv_byte)
			recv_string = recv_string.replace("[", '')
			recv_string = recv_string.replace("]", '')
			recv_string = recv_string.replace(",", '')
			recv_string = recv_string.replace(" ", '')
			#print "String:" + str(recv_string)
			recv_int = int(recv_string, 2)
			#print "Integer:" + str(recv_int)
			buchstabe = chr(recv_int)
			#print "Character:" + str(buchstabe)
			satz += str(buchstabe)
			#print "Satz:" + str(satz)
		f = open(target_file, "w")
		f.write(satz)
		f.close()
		return satz

	def close_connection(self):
		GPIO.cleanup()
