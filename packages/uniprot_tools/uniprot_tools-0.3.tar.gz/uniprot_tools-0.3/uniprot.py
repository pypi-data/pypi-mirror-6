"""
uniprot provides a command-line and python interface
to access the uniprot database

available services:
	map
	retrieve
"""

import requests
import sys, argparse

url = 'http://www.uniprot.org/'

def retrieve(query, format='txt'):
	""" request entries by uniprotid using batch retrieval
	
	Args:
		query: to be mapped
		format: txt by default
		
	Help:
		possible formats:
		txt, xml, rdf, fasta, gff"""
	tool = 'batch/'
	
	query = list(set(query.split()))
	queries = [query[i:i+100] for i in xrange(0, len(query), 100)]

	data = {'format':format}

	responses = [requests.post(url + tool, data=data, files={'file':' '.join(query)}) for query in queries]
	page = ''.join([response.text for response in responses])
	return page

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
	tool = 'mapping/'

	data = {
			'from':f,
			'to':t,
			'format':format,
			'query':query
			}
	response = requests.post(url + tool, data=data)
	page = response.text
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
