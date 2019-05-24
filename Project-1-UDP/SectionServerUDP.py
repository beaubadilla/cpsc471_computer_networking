#!/usr/bin/env python3
# ASCII values with chars > 1 byte messes up calc_num_sections algorithm
import sys
import socket
import hashlib
import os
import stat

PORT = 7037
N = 8								# Index which n in 'SECTION n' should be
MAX_SECTION_SIZE = 32768			# 32768
MAX_STRING_LENGTH_MD5 = 16			# Unit is bytes
MAX_UDP_PAYLOAD = 65507
MAX_NUM_SECTIONS_SEND = 1024

def calc_num_sections(my_file):
	"""Get file. Find size of file. Divide by ~32KiB. Return quotient. 
	Accounts for last section of 'imperfect' size."""
	file = my_file
	size_of_file = os.stat(file).st_size
	num_sections = int(size_of_file/MAX_SECTION_SIZE)
	if size_of_file % MAX_SECTION_SIZE != 0:
		num_sections += 1
	return num_sections, size_of_file


def recv_message():
	"""Create a socket. Bind it to an address(IP, PORT). Wait for a message to be received"""
	with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
		print("About to bind")
		s.bind(('', PORT))
		print("Now waiting...")
		message, client_address = s.recvfrom(MAX_UDP_PAYLOAD)
	return message.decode(), client_address

def send_message(message, client_address):
	with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
		s.sendto(message.encode(),client_address)

def fill_byte_array(my_file, bytearray):
	# Read file, read each line and append each character into the bytearray
	# Example: my_string = "Hello World"
	# bytearray.append(my_string)
	# bytearray = [72, 101, 108, 108, 111, 32, 87, 111, 114, 108, 100] # data type = int
	# Each index is the DEC (from ASCII Table) representation of the character
	file = my_file
	r_file = open(file, 'r')
	for line in r_file:
		bytearray.extend(line.encode())

def md5(section):
	"""Returns 32 hexdigit of a string"""
	this_section = section
	new_string = ""
	for x in range(len(this_section)):
		new_string += chr(this_section[x])
	m = hashlib.md5()
	m.update(new_string.encode())
	return m.hexdigest()

def md5File(bytes_of_file):
	m = hashlib.md5()
	m.update(bytes_of_file)
	return m.hexdigest()

def prep_section_message(section):
	this_section = section
	new_string = ""
	for x in range(len(this_section)):
		new_string += chr(this_section[x])
	return new_string

def create_section_list(num_sections, bytes_of_file, size_of_file):
	sections = []
	section = []
	byte_ctr = 0

	# Get every section besides last one and adds it to the list (sections)
	## Create a section based off the max size (32KiB)
	## Section 1 contains bytes_of_file[0] - bytes_of_file[31999]
	## Section 2 contains bytes_offile[32000] - bytes_of_file[63999]...etc
	## Add each section to the sections[]
	## sections = [section1, section2,...]

	for x in range(num_sections-1):
		section.clear()
		for y in range(MAX_SECTION_SIZE):
			section.append(bytes_of_file[byte_ctr])
			byte_ctr += 1
		sections.append((list(section)))

	# Get last section
	section.clear()
	size_of_last_section = size_of_file - ((num_sections-1)*MAX_SECTION_SIZE)
	for last_bytes in range(size_of_last_section):
		section.append(bytes_of_file[byte_ctr])
		byte_ctr += 1
	sections.append(section)

	return sections

def main():
	# After executing 'ServerSection.py testfile.gz'
	# sys.argv = ['ServerSection.py','testfile.gz']
	# therefore sys.argv[1] == 'testfile.gz'
	my_file = sys.argv[1]

	# Set up byte array to hold the data of the file
	num_sections, size_of_file = calc_num_sections(my_file)
	bytes_of_file = bytearray()
	fill_byte_array(my_file, bytes_of_file)
	section_list = create_section_list(num_sections, bytes_of_file, size_of_file)

	# Set up response message for 'LIST'
	# Set up (VERY LARGE) string of the format asked by the assignment
	response_list = ""
	# Get checksum of entire file
	response_list += md5File(bytes_of_file) + "\n"
	for num_s in range(num_sections-1):
		response_list += str(num_s) + " "
		response_list += str(MAX_SECTION_SIZE) + " "
		response_list += md5(section_list[num_s]) + "\n"
	if size_of_file%MAX_SECTION_SIZE != 0:
		response_list += str(num_sections-1) + " " + str((size_of_file%MAX_SECTION_SIZE)) + " " + md5(section_list[num_sections-1]) + "\n"



	while True:
		message, client_address = recv_message()
		split_string = message.split(" ", 1)
		if split_string[0] == 'LIST':
			print("The client has requested for the list.")
			send_message(response_list, client_address)
		elif split_string[0] == 'SECTION':
			requested_section = int(split_string[1])
			print("The client has requested section", requested_section)
			if requested_section < num_sections:
				response_section_n = ""
				response_section_n += prep_section_message(section_list[requested_section])
				send_message(response_section_n, client_address)
			else:
				print("That section does not exist.")
		else:
			print("Have fun with that text file. Goodbye")
			exit()

main()


#	  __________
#	_/PSEUDOCODE\__________________________________________________________________

# #   Prof executes python3 SectionServer.py testfile.gz
# #   Our program reads in the first argument 'testfile.gz', and loads the file
# #   Calculate num_sections
# #   Calculate size of last section
# #   Place each "section" into an array
# #   Prof (on Server.py) sends either "LIST" or "SECTION n"
# #   If LIST
# #       Display MD5 checksum
# #       for section in (num_sections - 1):
# #           Display section
# #           Display size_of_section
# #           Display MD5 checksum
# #    If SECTION n
# #       Parse string to find n
# #       Get section from array