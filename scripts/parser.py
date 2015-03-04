#!/usr/bin/env python

from StringIO import StringIO
import os
import os.path
import cPickle as pickle
import hashlib

path = 'results'
cache = None

def lst(typ):
	return lambda x : [typ(n) for n in x.split(',')]

def boolean(x):
	x = str(x).strip().lower()
	return x is 'true' or x is '1' or x is 'yes'

def empty(x):
	return []

types = {
	'time': int,
	'nOnceBurned': int,
	'nBurning': int,
	'iterations': int,
	'NCCCs': int,
	'MessageNum': int,
	'MessageBytes': int,
	'OtherNum': int,
	'OtherBytes': int,
	'score': float,
	'utility': float,
	'violations': int,
	'solvable': boolean,
	'utilities': empty,
	'final': float,
	'final_greedy': float,
	'best': float,
	'best_greedy': float,
	'cpu_time': int,
}

def cache_key(*args):
	return hashlib.md5(str(args)).hexdigest() + '.cache'

def load_problems_cached(selectors):
	k = cache_key(selectors)
	f = os.path.join(path, k)
	if os.path.isfile(f):
		return pickle.load(open(f, 'rb'))

	problems = load_problems(selectors)
	pickle.dump(problems, open(f, 'wb'))
	return problems

def load_problems(selectors):
	def selected(problem):
		settings = problem[0]
		for key, value in selectors:
			if not key in settings:
				return False
			if hasattr(value, '__iter__'):
				if settings[key] not in value:
					return False
			else:
				if settings[key] != value:
					return False
		return True

	ps = load_all_problems()
	result = filter(selected, ps)
	return result

def load_all_problems():
	def is_result_file(x):
		return os.path.isfile(x) and x.endswith('.dat')

	global cache
	if cache is None:
		f = os.path.join(path, 'all.cache')
		if os.path.isfile(f):
			cache = pickle.load(open(f, 'rb'))
		else:
			files = filter(is_result_file, map(lambda x: os.path.join(path, x), os.listdir(path)))
			cache = [parse_problem(x) for x in files]
			cache.sort(key=lambda x: x[0]['solver'])
			pickle.dump(cache, open(f, 'wb'), -1)
	return cache

def load_selectors(excludes=[]):
	settings, _ = zip(*load_all_problems())
	# Get a set of tuples with unique settings
	settings = set(tuple((k,v) for k,v in s.items() if k not in excludes) for s in settings)
	return settings


def parse_problem(f, filtr=None):
	def parse(row):
		raw = row.split()
		foo = dict([(hdr, types[hdr](raw[idx])) for idx,hdr in enumerate(headers)])
		return foo
	def parse_setting(line):
		return [field.strip(':') for field in line.split()[1:]]

	print "Parsing", f
	settings = StringIO()
	settings.writelines(line for line in open(f, 'r') if line.startswith("#"))
	settings.seek(0)
	settings = dict([parse_setting(line) for line in settings])

	if filtr is not None and not filtr(settings):
		return None

	data = StringIO()
	data.writelines(line for line in open(f, 'r') if not line.startswith("#"))
	data.seek(0)
	headers = data.next().split()
	return settings, [parse(row) for row in data]
