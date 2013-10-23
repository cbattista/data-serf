#plot_	config.py
import numpy
import random

class smartDict(dict):
	def __init__(self, *args, **kwargs):
		self.d = {}
		self.returnBlank = False

	def __getitem__(self, key):
		if self.d.has_key(key):
			return self.d[key]
		else:
			if not self.returnBlank:
				self.d[key] = key.replace('_', ' ')
			else:
				self.d[key] = ""
			return self.d[key]
	
	def __setitem__(self, key, value):
		self.d[key] = value


class colorDict(smartDict):
	def __setitem__(self, key, value):
		self.d[key] = numpy.array(value)
		self.inverted = False

	#allow the inversion of colour (for printing slides)
	def invert(self):
		d = self.d
		for k in self.d.keys():
			d[k] = 1 - d[k]

		self.inverted = True

	def __getitem__(self, key):
		if self.d.has_key(key):
			return self.d[key]
		else:
			if not self.returnBlank:
				#self.d[key] = key.replace('_', ' ')
				r = random.choice(range(0, 101)) / 100.
				g = random.choice(range(0, 101)) / 100.
				b = random.choice(range(0, 101)) / 100.
				self.d[key] = [r, g, b]
			else:
				self.d[key] = ""
			return self.d[key]
		
"""
SLIDE SETTINGS
figsize = [6, 4.5]

title_font = {'color' : 'k', 'fontsize' : 24}
axis_font = {'color' : 'k', 'fontsize' : 18}
tick_size = 14
leg_font = {'size':'large'}

fontsize = 40
prop = {'size': fontsize}

marker_size = 60
line_width=2
"""

figsize = [4.5, 4.5]
title_font = {'color' : 'k', 'fontsize' : 12}
axis_font = {'color' : 'k', 'fontsize' : 10}
tick_size = 11
leg_font = {'size':'large'}

fontsize = 12
prop = {'size': fontsize}

marker_size = 30
line_width=1


mdict = {}
mdict['calc'] = 'o'
mdict['mem'] = 's'

scores = smartDict()
scores['RT'] = 'reaction times'
scores['RTs'] = 'reaction times'
scores['ACC'] = 'accuracies'
scores['solution'] = 'sums'
scores['zRT'] = 'normalized reaction times'
scores['zsolution'] = 'normalized solution sizes'
scores['conv'] = 'conversion'
scores['strat'] = 'strategy'

units = smartDict()
units.returnBlank = True
units['RT'] = 's'
units['ACC'] = '%'
units['RTs'] = 's'

titles = smartDict()
titles['pre'] = "pre training"
titles['CAT3'] = "Experiment 2"
titles['CAT2'] = "Experiment 1"
titles['training'] = "training task"
titles['post'] = "post training"
titles['novel'] = "untrained"
titles['trained'] = "trained"
titles["{'$exists': True}"] = "all"
titles["CAT2"] = "Experiment 1"
titles["CAT3"] = "Experiment 2"
titles["solution"] = 'sum'
titles['RT'] = 'reaction time (s)'
titles['RTs'] = 'reaction time (s)'
titles['ACC'] = 'accuracy (%)'
titles['pre_pro_strat_label'] = 'Within Task Strategy'
titles['post_pro_strat_label'] = 'Within Task Strategy'
titles['pre_day_strat_label'] = 'Between Task Strategy'
titles['post_day_strat_label'] = 'Between Task Strategy'
titles['pre_ver_strat_label'] = 'Within Task Strategy'
titles['conv'] = 'conversion'
titles['strat'] = 'strategy'
titles['trained'] = 'training'
titles['tconv'] = ''
titles['tcm'] = 'recent mem'
titles['ncc'] = 'untrained calc'
titles['nmm'] = 'remote mem'
titles['ncm'] = 'untrained recent mem'
titles['tcc'] = 'trained calc'
titles['tmm'] = 'trained remote mem'
titles['cond'] = 'condition'
titles['beta'] = 'beta weight'

cdict = colorDict()

cdict['calc'] = [0., 0., 1.]
cdict['c'] = cdict['calc']
cdict['cc|c'] = cdict['calc']
cdict['c_c'] = cdict['calc']
cdict['ncc'] = cdict['calc']
cdict['calc->calc-mem'] = [0., .5, .5]
cdict['calc->mem-calc'] = [.2, 0., .8]
cdict['novel'] = [.7, .4, .2]
cdict['trained'] = [.2, .4, .7]
cdict['cc'] = cdict['calc']


cdict['1'] = [0, 1, 0]
cdict['0'] = [1, 0, 0]

cdict['tmm'] = [1.,0,1.]

cdict['ncm'] = [1, 1, 0]
cdict['tcc'] = [1, 0.5, 0]
cdict['cm'] = [0, 0, 0]
cdict['c|m'] = cdict['cm']
cdict['cm|m'] = cdict['cm']
cdict['cm|c'] = cdict['mc']

cdict['mc'] = [.1,.1,.1]
cdict['m-c'] = cdict['mc']
cdict['nmc'] = cdict['mc']
cdict['Error'] = cdict['mc']
cdict['tmc'] = cdict['mc']
cdict['m|c'] = cdict['mc']
cdict['mc|c'] = cdict['mc']
cdict['mc|m'] = cdict['mc']
cdict['cm|c'] = cdict['mc']

cdict['tcm'] = [0., 1., 0.]

cdict['mem'] = [1., 0., 0.]
cdict['mm'] = cdict['mem']
cdict['m'] = cdict['mem']
cdict['m_m'] = cdict['mem']
cdict['mm|m'] = cdict['mem']
cdict['mem->calc-mem'] = [.5, .5, 0.]
cdict['mem->mem-calc'] = [.8, 0., .2]
cdict['nmm'] = cdict['mem']

cdict['pre'] = [1., 1., 1.]
cdict['post'] = [0., 0., 0.]
cdict['False'] = [0.1, 0.1, 0.1]
cdict['True'] = [0.7, 0.7, 0.7]

limit = {}
#limit['RT'] = None
limit['RT'] = {'RT': {'$lte': 4}}
limit['zRT'] = {'zRT': {'$lte':3, '$gte':-3}}
limit['trained'] = {'trained': {'$ne': 'untrained'}}
limit['solution'] = None
limit['zsolution'] = None
limit['avgRT'] = {'zRT': {'$lte':3, '$gte':-3}}
limit['deltaRT'] = None

hatches ={}
hatches['novel'] = '/'
hatches['trained'] = ''
hatches['pre'] = '\\'
hatches['post'] = ''
hatches['all'] = None
hatches['True'] = ''
hatches['False'] = '/'

orders = {}
orders['strat'] = ['mem', 'calc']
orders['conv'] = ['m_m', 'c_m', 'c_c']
orders['day'] = ['pre', 'post']
orders['tconv'] = ['tmm', 'nmm', 'tcc', 'ncc']


