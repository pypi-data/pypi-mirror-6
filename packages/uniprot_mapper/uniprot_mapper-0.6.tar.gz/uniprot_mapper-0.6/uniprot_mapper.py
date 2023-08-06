#!/usr/bin/env python
import urllib,urllib2
import sys, argparse

def map(query, f, t, format='tab'):
	""" map a string of whitespace seperated entries from
	one format onto another using uniprots mapping api
	
	Args:
		query: to be mapped
		f: from ACC | P_ENTREZGENEID | ...
		t: to ...
		format: tab by default
	
	Help:
		for a list of all possible mappings visit
		'http://www.uniprot.org/faq/28'
	"""
	url = 'http://www.uniprot.org/mapping/'

	params = {
			'from':f,
			'to':t,
			'format':format,
			'query':query
			}

	data = urllib.urlencode(params)
	request = urllib2.Request(url, data)
	response = urllib2.urlopen(request)
	page = response.read()
	return page

if __name__ == '__main__':
	
	parser = argparse.ArgumentParser(description='retrieve uniprot mapping')
	parser.add_argument('f', help='from')
	parser.add_argument('t', help='to')
	parser.add_argument('inp', nargs='?', type=argparse.FileType('r'),
			default=sys.stdin, help='input file (default: stdin)')
	parser.add_argument('out', nargs='?', type=argparse.FileType('w'),
			default=sys.stdout, help='output file (default: stdout)')
	parser.add_argument('--format', default='tab', help='output format')
	
	args = parser.parse_args()

	query = args.inp.read()
	args.out.write(map(query, args.f, args.t))
