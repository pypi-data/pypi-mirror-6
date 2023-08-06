# uniprot mapper

map a string of whitespace seperated entries from
one format onto another using uniprots mapping api

	Args:
		query: to be mapped
		f: from ACC | P_ENTREZGENEID | ...
		t: to ...
		format: tab by default

	Help:
		for a list of all possible mappings visit
		'http://www.uniprot.org/faq/28'

## Installation

### From pypi (recommended)
	pip install uniprot_mapper

### From source (UNIX) as standalone only
Clone the git repository

	git clone https://github.com/jdrudolph/uniprot_mapper.git

Make the script executable and add it to your `PATH`:
	
	chmod +x uniprot_mapper/uniprot_mapper/uniprot_mapper.py
	cd /usr/local/bin
	sudo ln -s /path/to/uniprot_mapper.py uniprot_mapper

## Example

### standalone
	
	uniprot_mapper ACC P_ENTREZGENEID acc_file map_file

This will read UniprotIDs seperated by whitespaces 
from `acc_file` and store them to `map_file`.

Using a pipe:

	echo P31749 | uniprot_mapper ACC P_ENTREZGENEID

will print the result to `stdout` which can be redirected
further

### inside a python script

	import uniprot_mapper as mapper
	print mapper.map('P31749')
