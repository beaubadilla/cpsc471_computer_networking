# For Professor Avery:
# If the server has 'zeros', it works 100%
# If the server has 'bigfile', it works 99%. The 1% being the very last packet not passing the checksum verification.
#	Therefore, it will infinitely loop.
# ----------------------------------------------------------------------------------------------------------------------
#!/usr/bin/env python3

import sys
import math
import socket
import random
import hashlib
import datetime

DEFAULT_PORT = 7037
SIZE_1_KiB = 1024
SIZE_32_KiB = 32 * SIZE_1_KiB
MAX_SECTION_SIZE = SIZE_32_KiB
BUFFER_SIZE = 32768

def parse_address(address):
	"""Separate IP addrees and Port #"""
	components = address.split(':', maxsplit=1)
	hostname = components[0]
	port = DEFAULT_PORT if len(components) == 1 else int(components[1])

	return (hostname, port)

def decode_list_response(list_response):
	"""Takes in the response from a 'LIST' request, separates each category into a 5 element list, then 
	appends that list into the 'sections' list"""
	lines = list_response.decode().splitlines()

	expected_file_digest = lines.pop(0)
	sections = []
	total_file_size = 0

	for line in lines:
		columns = line.split(maxsplit=2)
		section_num = int(columns[0])
		beg_byte = int(section_num * MAX_SECTION_SIZE)
		end_byte = int((section_num+1) * MAX_SECTION_SIZE)
		section = list((columns[0], columns[1], columns[2], beg_byte, end_byte))
		sections.append(section)
		total_file_size += int(columns[1])

	return expected_file_digest, sections, total_file_size


def md5(section):
	"""Receives bytes, returns checksum"""
	m = hashlib.md5()
	m.update(section)
	return m.hexdigest()

def main(server_address, filename):
	# TCP Connection
	server_ip, port = parse_address(server_address)
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((server_ip, port))
	print("Connected s1")

	# LIST request
	s.send('LIST'.encode())
	list_response = s.recv(BUFFER_SIZE)
	# print(list_response)
	expected_file_digest, sections, total_file_size = decode_list_response(list_response)

	# Bytearray to store downloaded file
	file_contents = bytearray(total_file_size)

	# Handle post-LIST request
	s.close()

	# Download file
	for section in sections:

		print("Connected s2")
		print("Section: " + str(section[0]))

		# Loop until no error
		error = True
		while error:
			error = False
			s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s2.connect((server_ip, port))
			section_request_string = "SECTION " + str(section[0])
			s2.send(section_request_string.encode())	# response are bytes
			downloaded_section = s2.recv(min(total_file_size - section[3],BUFFER_SIZE))

			# Check for any type of error(size, checksum, 'ERROR')
			#	Check size
			downloaded_section_size = len(downloaded_section)
			downloaded_section_digest = md5(downloaded_section)
			str_downloaded_section = downloaded_section.decode("utf-8")		# returns string representation of the downloaded section
			split_str_downloaded_section = str_downloaded_section.split(":")
			# 	Check for "Error:"
			if split_str_downloaded_section[0] == 'ERROR':
				print("Received ERROR: ; reconnecting")
				error = True
				s2.close()
				continue
			if downloaded_section_size != int(section[1]):
				print("Expected section size: " + str(section[1]) + "\t Received: " + str(downloaded_section_size))
				error = True
				s2.close()
				continue
			#	Check checksum
			if downloaded_section_digest != str(section[2]):
				print("Expected section digest: " + str(section[2]) + "\t Received: " + str(downloaded_section_digest))
				error = True
				s2.close()
				continue
			


		file_contents[section[3]:section[4]] = downloaded_section
		print("Section # " + str(section[0] + " successful"))

		# Reset error flag
		error = True
		s2.close()

	# Verify the file was properly downloaded
	downloaded_file_digest = md5(file_contents)
	if downloaded_file_digest != expected_file_digest:
		print("Digest expected: " + str(expected_file_digest) + "\t Received: " + str(downloaded_file_digest))
	else:
		print("File download successful")
		with open(filename, 'wb') as f:
			f.write(file_contents)

main('localhost', '471download.txt')

#	__________
#__/PSEUDOCODE\_____________________________________
# Execute 'SectionServer.py'
# Execute 'SectionClient.py'
# Connect with sockets
# Client sends 'LIST' request
# Server returns list(index, size, digest)
# Client gets file digest (from list), # of sections (calc from list)
# Server also holds its own copy of the list to compare for later
# Connect again with socket (after LIST request, connection closes)
# Begin requesting sections
#	If response contains 'ERROR'
#		request section again
#	else
# 		compare response with checksums from the copied LIST response
#	 	if checksums do not match
#			request section again

#  	______________
#__/INFO FOR LATER\____________
# For the client to receive messages(in bytes) from server: socket_name.recv(buffer_size)
# "Copy" of list is 'sections'
# sections[n][0] = number of section
# sections[n][1] = size of section
# sections[n][2] = checksum of section
# sections[n][3] = beginning byte number of section
# sections[n][4] = end byte number of section

# Can download a file from SectionServer.py
# Verifies that the file was successful
# Handle failed download requests

# Note:
# Connection will close after LIST request
# Connection will stay open after SECTION requests
# Failed requests will return a response (from Server) with 'ERROR' in the beginning