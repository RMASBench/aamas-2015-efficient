#!/usr/bin/env python

import parser
import numpy as np
import pickle

parser.path = '../results'
util_field = 'utility'
scen_field = 'score'
algorithms = ['DSA', 'BinaryMaxSum', 'Greedy']
reports = [
	('score', 'final'),
	('nOnceBurned', 'final'),
	('time', 'final'),
	('NCCCs', 'aggregate'),
	('MessageNum', 'aggregate'),
	('MessageBytes', 'aggregate'),
	('iterations', 'aggregate'),
	('converged', 'converged'),
	('cpu_time', 'aggregate'),
]
extras = {
	'MessageNum': 'OtherNum',
	'MessageBytes': 'OtherBytes',
}
selector_names = [
	(['main_solver'], 'Solver'),
	(['agent.interteam'], 'IT'),
	(['map.scenario'], 'Scenario'),
]


def stats(selectors):
	def collect(key, t):
		if t == 'final':
			return final_scenario_stats(main_problems, key)
		if t == 'aggregate':
			extra = extras[key] if key in extras else None
			return aggregate_scenario_stats(main_problems, key, extra)
			return zip(*[wins(problems[a], algs) for a in algs])
		if t == 'converged':
			return converged_scenario_stats(main_problems, key)

	problems = parser.load_problems(selectors + [('solver', algorithms),])
	if not problems:
		raise Exception("No problems matching selectors " + str(selectors))
	if len(problems) != 1:
		raise Exception("What the fuck selectors " + str(selectors) \
			+ " yields " + str(len(problems)) + " problems: \n" + \
			str(problems[0][0]) + "\n" + str(problems[1][0]))

	main_problems = dict([(p[0]['main_solver'],p) for p in problems if p[0]['main_solver'] == p[0]['solver']])

	return dict((key,collect(key,t)) for key,t in reports)

def scenario_stats(selectors, results):
	def collect(values, t):
		if t == 'aggregate':
			return [x for y in values for x in y]
		return values

	rkeys = [key for key,t in reports]
	results = dict((key, zip(*[result[key] for result in results])) for key in rkeys)

	result = {}
	for key,t in reports:
		values = collect(results[key][0], t)
		result[key] = values			
	
	return result

def print_results(results):
	def name(ks):
		key = [k for k in ks if k in s]
		return s[key[0]] if key else '-'
	def names(selectors):
		return [name(ks) for ks,n in selector_names]

	def prettify(vs):
		return "%.5f [+-%.5f]" % (np.mean(vs), np.std(vs)/np.sqrt(len(vs)))

	print "\t".join([n for ks,n in selector_names] + [key for key,_ in reports])
	for selectors, values in results.items():
		s = dict(selectors)
		print "\t".join(names(selectors) + [prettify(values[key]) for key,_ in reports])

def iff(fun, values):
	v = fun(values)
	return [1 if x == v else 0 for x in values]

def ifmax(x):
	return iff(max, x)

def argmaxval(x):
	xmax = max(x)
	return x.index(xmax), xmax

def argmaxvald(x):
	l = sorted(x.items(), key=lambda y: y[1])
	return l[-1]

def wins(problems, algs):
	def fetch(algo, problems):
		for settings, values in problems:
			if settings['solver'] == a:
				return values
	pdata = [fetch(a, problems) for a in algs]

	values = [[row[util_field] for row in p] for p in pdata]
	total  = len([row[util_field] for row in pdata[0]])
	counts = map(sum, zip(*map(ifmax,zip(*values))))
	counts = [float(count) / total * 100 for count in counts]
	return counts

def final_scenario_stats(problems, key):
	return [problems[a][1][-1][key] for a in algorithms if a in problems.keys()]

def aggregate_scenario_stats(problems, key, extra):
	if extra:
            return [[np.array(x[key]) + np.array(x[extra]) for x in problems[a][1]] for a in algorithms if a in problems.keys()]
	return [[x[key] for x in problems[a][1]] for a in algorithms if a in problems.keys()]

def converged_scenario_stats(problems, key):
	return [len([1 for x in problems[a][1] if x['iterations'] < 100])/float(len(problems[a][1])) \
		for a in algorithms if a in problems.keys()]

def parse_args(args):
	args = ' '.join(args)
	selectors, fields = args.split('--')
	print selectors, fields
	selectors = [s.split('=') for s in selectors.split()]
	return selectors, fields.split()

if __name__ == '__main__':
	selectors = parser.load_selectors(['random.seed', 'run'])
	seeds = map(str, xrange(1, 31))

	results = {}
	for s in selectors:
		parts = [stats(list(s) + [('random.seed', seed)]) for seed in seeds]
		results[s] = scenario_stats(s, parts)

	pickle.dump(results, open( "results.p", "wb" ) )
	print_results(results)
