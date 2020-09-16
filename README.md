<br />
<p align="center">
  <h1 align="center">Computer Networking Protocols and Concepts</h1>

  <p align="center">
    Implementations of the TCP and UDP networking protocol.<br/>
    Projects for <a href="http://www.fullerton.edu/">Cal State Fullerton</a>'s Computer Networking course(CPSC 471).
    <br />
    <a href="https://github.com/beaubadilla/cpsc471_computer_networking/issues">Report Bug or Request Feature</a>
  </p>
</p>

## Table of Contents

* [About the Project](#about-these-projects)
  * [Technologies](#technologies)
  * [Code Snippets](#code-snippets)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [License](#license)
* [Contact](#contact)

## About these Projects

 Throughout the course, we covered networking concepts related to most of the layers of the **open systems interconnection(OSI) model**. With these three projects, we concentrated on the transport layer(i.e. layer 4). In a group of three, we implemented several programs with each project having a focus on a networking protocol or architecture. Related concepts: **hashing algorithms, message digests, checksums**

* **Project-1-UDP**: Implemented a file download program as the server under the ***user datagram protocol(UDP)***.
* **Project-2-TCP**: Implemented a file download program as the client under the ***transmission control protocol(TCP)***
* **Project-3-P2P**: Implemented a file sharing program through a ***peer-to-peer*** network.


### Technologies
Languages: Python 3.x

Modules:
* [socket](https://docs.python.org/3/library/socket.html)
* [hashlib](https://docs.python.org/3/library/hashlib.html)
* [selectors](https://docs.python.org/3/library/selectors.html)

### Code Snippets
/Project-1-UDP/SectionServerUDP.py: Utilizing md5 hash as a checksum to verify the integrity of the data
```python
def md5(section):
	"""Returns 32 hexdigit of a string"""
	this_section = section
	new_string = ""
	for x in range(len(this_section)):
		new_string += chr(this_section[x])
	m = hashlib.md5()
	m.update(new_string.encode())
	return m.hexdigest()
```

/Project-2-TCP/SectionClientTCP.py: Acting as the client, we extract the metadata from the response of the server
```python
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
```

/Project-3-P2P/SectionClientP2P.py: Multiplexing with selectors
```python
while not download_complete:
  for key, mask in sel.select(timeout=None):
      connection = key.fileobj
      data = key.data
      if mask & selectors.EVENT_READ:
          recv_data = connection.recv(1024)
          if recv_data:
              data.data[beg_byte:(beg_byte+len(recv_data))] = recv_data
              beg_byte += len(recv_data)
          else:
              sel.unregister(connection)
              connection.close()
```
## Getting Started

### Prerequisites

Download [Python 3.x](https://www.python.org/downloads/)

### Installation

1. Clone the repo
```sh
git clone https://github.com/beaubadilla/cpsc471_computer_networking.git
```
2. Follow the README.md for each individual part.

## License
[MIT](https://choosealicense.com/licenses/mit/)

## Contact

Beau Jayme De Guzman Badilla - beau.badilla@gmail.com - [LinkedIn](https://www.linkedin.com/in/beau-jayme-badilla/)
