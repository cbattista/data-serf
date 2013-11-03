import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

from mt import WriteTable, ReadTable, MongoAdmin
import os
from plot_config import *

def safePath(path):
	path = path.replace(' ', '_')
	path = path.replace(':', '')
	path = path.replace(',', '')
	path = path.replace('>', '_')
	path = path.replace('$', '')
	path = path.replace('[', '')
	path = path.replace(']', '')
	path = path.replace('{', '')
	path = path.replace('}', '')
	path = path.replace("'", "")
	return path	


class plot():
	def __init__(self, db, table, DV, IV, condition={}, title = "", fmt = 'paper', colordict=None, legend=True, sigs = None, show=False, figsize = None, subplot=False):
		self.db = db
		self.table = table
		self.DV = DV
		self.IV = IV
		self.fmt = fmt
		self.legend = legend
		self.condition = condition
		self.subplot=subplot
		if sigs:
			if type(sigs[0]) == list:
				self.sigs=sigs
			else:
				self.sigs = [sigs]
		else:
			self.sigs = sigs
		self.show = show
		self.figsize = figsize
		if not colordict:
			self.cdict = cdict
			if fmt == 'slide':
				if not self.cdict.inverted:
					self.cdict.invert()
		else:
			self.cdict = colordict
				

		#set the title
		if not title:
			row = MongoAdmin(db).getTable(table).posts.find_one(condition)
			if row:
				if row.has_key('title'):
					title = row['title']

		self.title = title
		self.fig_format = 'png'

		#fonts and sizes
		if self.fmt == 'slide':
			if not self.figsize:
				self.figsize = [4, 4.5]
			#self.cdict.invert()
			self.tick_size = 14
			self.title_font = {'color' : 'k', 'fontsize' : 18}
			self.axis_font = {'color' : 'k', 'fontsize' : 16}
			self.leg_font = {'size':'x-large'}
		elif self.fmt == 'plos_pub':
			if not self.figsize:
				self.figsize = [3.27, 3.27]
			self.title_font = {'color': 'k', 'fontsize': 12}
			self.axis_font = {'color' : 'k', 'fontsize' : 10}
			self.tick_size = 10
			self.leg_font = {'size':'8'}
			self.fig_format = 'png'
		else:
			if not self.figsize:
				self.figsize = [2.25, 2.5]
			self.title_font = {'color' : 'k', 'fontsize' : 10}
			self.axis_font = {'color' : 'k', 'fontsize' : 9}
			self.tick_size = 9
			self.leg_font = {'size':'x-small'}

		#set the file name
		#self.fname = "%s_%s_%s_%s_%s.%s" % (db, table, DV, IV, str(condition), fig_format)

		#create dat figure
		if not self.subplot:
			self.fig = plt.figure(figsize=self.figsize, dpi=300)

			#create dat axis
			self.ax = plt.subplot(111)
	
		self.__db__()


	def __label__(self, x="", y="", pos=""):
		if not x:
			x = self.DV
		if not y:
			y = self.IV
		print x, y
		plt.ylabel(titles[x],fontdict=self.axis_font)
		plt.xlabel(titles[y], fontdict=self.axis_font)
		plt.yticks(fontsize=self.tick_size)
		plt.xticks(fontsize=self.tick_size)

		if not self.subplot:
			if self.legend:
				box = self.ax.get_position()
				self.ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
				if not pos:
					plt.legend(loc='upper center', prop=self.leg_font, bbox_to_anchor=(0.5, 0), ncol = 2)
				else:
					plt.legend(loc=pos, prop=self.leg_font)

		plt.title(self.title, fontdict=self.title_font)

	def __db__(self):
		w = WriteTable([self.DV], self.IV, self.condition, self.db, self.table, subject="sid")
		self.fname = w.name

		if not os.path.exists("output/%s.dat" % self.fname):
			w.Compute()
			w.WriteForR()

		self.posts = ReadTable("output/%s.dat" % self.fname, self.db, "bars", clear=True).posts

	def __style__(self, path):
		if self.fmt == 'slide':
			#invert dat image
			print path
			os.system("convert %s.png -negate %s.png" % (path, path))
			if self.show:
				plt.show()

	def __savefig__(self, path):
		if not self.subplot:
			bbox_inches='tight'
			plt.savefig("%s.%s" % (path, self.fig_format), bbox_inches='tight')
			plt.savefig("%s.svg" % path, bbox_inches='tight')

#class scatter(db, table, DV1, DV2, IV, condition={}, connect=False, loc='upper right', title='', fromFile=False, xlim=[], ylim=[]):

class scatter(plot):
	def __init__(self, *args, **kwargs):
		plot.__init__(self, *args, **kwargs)

	def __db__(self):
		w = WriteTable(self.DV, self.IV, self.condition, self.db, self.table, subject="sid")

		fname = "output/%s.dat" % w.name
		if not os.path.exists(fname):
			w.Compute()
			w.WriteForR()
	
		r = ReadTable(fname, self.db, "scatter", clear=True) 
	
		self.posts = MongoAdmin(self.db).getTable("scatter").posts

	def draw(self):
		IV = self.IV
		DV1 = self.DV[0]
		DV2 = self.DV[1]	
		db = self.db
		table = self.table	
		condition = self.condition
		posts = self.posts

		if IV:
			if orders.has_key(IV):
				levels = orders[IV]
			else:
				levels = posts.distinct(IV)

			print levels

			sLines = {}

			for l in levels:
				xs = []
				ys = []
				for row in posts.find({IV:l}):
					x = row[DV1]
					y = row[DV2]
					xs.append(x)
					ys.append(y)

					k = str(row['sid'])
					if sLines.has_key(k):
						sLines[k][0].append(x)
						sLines[k][1].append(y)
					else:
						sLines[k] = [[x], [y]]

				print xs, ys
				plt.scatter(xs, ys, label=l, s=marker_size, color=cdict[l])
		else:
			xs = []
			ys = []
			sLines = {}
			for row in posts.find():
					x = row[DV1]
					y = row[DV2]
					xs.append(x)
					ys.append(y)

					k = str(row['sid'])
					if sLines.has_key(k):
						sLines[k][0].append(x)
						sLines[k][1].append(y)
					else:
						sLines[k] = [[x], [y]]
			plt.scatter(xs, ys, s=marker_size)

			

		for k in sLines.keys():
			plt.plot(sLines[k][0], sLines[k][1], color='k', alpha=0.25, linewidth=line_width)	

		self.__label__(DV2, DV1, pos='lower right')

		path = "output/scatter/%s_%s_%s_%s_%s_%s" % (db, table, DV1, DV2, IV, str(condition))

		path = safePath(path)

		self.__savefig__(path)
		self.__style__("%s.png" % path)
		self.path = "%s.png" % path


class bar(plot):
	def __init__(self, *args, **kwargs):
		print args, kwargs
		plot.__init__(self, *args, **kwargs)

	def draw(self, subplot = False):
		posts = self.posts

		plt.xticks([], fontsize=self.tick_size)

		# of subjects
		N = len(posts.find().distinct('sid'))

		print self.IV


		levels = posts.distinct(self.IV)
		levels.sort()

		sLines = {}

		xcount = 1

		ticks = []


		allYs = []
		allErrs = []
		allXs = []

		for l in levels:
			Xs = []
			Ys = []
			Yerr = []
			ys = []


			for row in posts.find({self.IV:l}):
				ys.append(row[self.DV])

			Ys.append(plt.mean(ys))
			allYs += Ys
			Yerr.append(plt.std(ys) / (N ** 0.5))
			allErrs += Yerr
			Xs.append(xcount)		
			allXs += Xs
			xcount += 1
			ticks.append(xcount - 0.5)
			plt.plot([0, len(levels)+2], [0, 0], color='k')
			plt.bar(Xs, Ys, yerr=Yerr, color=self.cdict[l], ecolor='k', label=titles[str(l)], width = 0.5)		

		plt.xlim([0.5, len(levels)+1])
		#plt.ylim([0.4, 1.2])

		#get min, max Y

		maxY = max(allYs) + allErrs[allYs.index(max(allYs))]
		minY = min(allYs) + allErrs[allYs.index(min(allYs))]
		
		span = maxY - minY

		ypush = span * .1

		if max(allYs) > 0:
			maxY = max(allYs) + allErrs[allYs.index(max(allYs))] + ypush
		else:
			maxY = ypush

		minY = min(allYs) - allErrs[allYs.index(min(allYs))] - ypush

		plt.ylim([minY - ypush, maxY + ypush])

		print "hello", self.sigs

		#draw the significant differences
		if self.sigs:
			push = span * .1
			siglist = []
			for s in self.sigs:
				x1 = levels.index(s[0]) + 1.25
				x2 = levels.index(s[1]) + 1.25
				xs = [x1, x2]
				xs.sort()
				#get the widths
				sig_w = abs(x2 - x1)
				siglist.append((xs[0], xs[1], sig_w))
			d = [('x1', float), ('x2', float), ('w', float)]
			siglist = numpy.array(siglist, dtype=d)
			x1  = siglist[0]
			maxX = max(allXs) + .25
			minX = min(allXs) + .25

			x1s = []
			x2s = []

			for sig in siglist:
				print sig
				if sig[0] == minX and sig[1] == maxX:
					x2s.append(sig)
				elif sig[0] == minX:
					x1s.append(sig)
				else:
					x2s.append(sig)

			x1s = numpy.array(x1s, dtype = d)
			x2s = numpy.array(x2s, dtype = d)

			x1s = numpy.sort(x1s, order= ['x1', 'x2'])
			x2s = numpy.sort(x2s, order= ['x2', 'w'])

			siglist = numpy.concatenate([x1s, x2s])

			print siglist

			for sigs in siglist:
				x1 = sigs[0]
				x2 = sigs[1]
				#horiz
				plt.plot([x1, x2], [maxY + push, maxY + push], 'k-')
				#vert 1
				plt.plot([x1, x1], [maxY-(ypush/2) + push, maxY + push], 'k-')
				#vert 2				
				plt.plot([x2, x2], [maxY-(ypush/2) + push, maxY + push], 'k-')
				push += ypush

			plt.ylim([minY - ypush, maxY + push])

		self.__label__()

		path = self.fname
		path = safePath(path)

		self.__savefig__("bars/%s" % path)
		self.__style__("bars/%s" % path)

