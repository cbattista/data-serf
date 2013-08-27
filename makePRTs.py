"""
the dataserf - a digital laborer for behavioral scientists
Copyright (C) 2013 Christian Battista

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import random
import pickle
import mt

def StringToType(value):
	if value.isdigit():
		val = int(value)
		
	elif value.count('.') == 1:
		val = value.split('.')
		if val[0].isdigit() and val[1].isdigit():
			val = float(value)

	else:
		val = value

	return val

def strip(item):
	item = item.strip()
	item = item.strip("\"")
	return item

class prtFile:
	def __init__(self, table, sid, run, settings = "", onset_start = 16000, offset=1950, checkErrors=False, source="eprime", duration=2, TR = 2.0, skippedTRs=2):
		self.settings = settings
		self.onset_start = onset_start
		self.offset = offset
		self.checkErrors = checkErrors
		self.table = table
		self.sid = sid
		self.run = run
		self.duration = duration
		self.TR = TR
		self.skippedTRs=skippedTRs
		self.posts = mt.MongoAdmin("datamaster").db[table].posts
		self.subjects = self.posts.distinct(sid)
		self.fileList = []

	def make(self, field, conditions, stim_onset, acc="ACC", rt="RT", trial="trial", balance = True, name=""):
		posts = self.posts

		for subject in self.subjects:
			runs = posts.find({self.sid : subject}).distinct(self.run)
			for run in runs:
				prtDict = {}

				if self.checkErrors:
					prtDict['Error'] = []
					longestRT = 0


				#q = {self.sid : subject, self.run : run, rt : {'$exists':True}}

				#get rows
				rows = posts.find({self.sid : subject, self.run : run}).sort(trial, 1)

				#calculate subtractor
				subtractor = self.onset_start - rows[0][stim_onset]

				print subject, run, subtractor, rows[0][stim_onset]
				
				for row in rows:
					proceed = True
					try:
						RT = row[rt]
						onset = row[stim_onset] + subtractor
						onset = int(onset)

						myCond = row[field]
						
					except:
						proceed = False
			
					if proceed:

						if balance:
							balString = conditions[0]
							for c in conditions[1:]:
								balString += "_%s" % c
							balString += "_bal"

							if not row[balString]:
								myCond = 'Error'

						if conditions:
							if myCond not in conditions:	
								myCond = 'Error'

						if onset != "":
							offset=onset+self.offset

							myString = "%s %s" % (onset, offset)

							if self.checkErrors:
								ACC = row[acc]
								if prtDict.has_key(myCond):
						
									if int(ACC):
										prtDict[myCond].append(myString)
									else:
										prtDict['Error'].append(myString)
								else:
									if int(ACC):
										prtDict[myCond]= [myString]
									else:
										prtDict['Error'].append(myString)

								if ACC:
									if RT > longestRT:
										longestRT = RT
										longCond = myCond
										longIndex = len(prtDict[myCond]) -1 

							else:
								if prtDict.has_key(myCond):
									prtDict[myCond].append(myString)
								else:
									prtDict[myCond]= [myString]

				if self.checkErrors:
					if not prtDict['Error']:
						prtDict['Error'] = [prtDict[longCond][longIndex]]
						del prtDict[longCond][longIndex]

				for c in conditions:
					if not prtDict.has_key(c):
						prtDict[c] = []
			
				self.prtDict = prtDict
				self.setColors()
				self.makePRT()
				name = "%s_%s_%s_%s" % (self.table, field, subject, run)
				self.writePRT(name)
				#self.writeEV(name)

	#generate a list of colours from the prtDict
	def setColors(self):
		if not os.path.exists("conditions.col"):
			codeDict = {}
			for k in self.prtDict.keys():
				R = random.randint(0, 255)
				G = random.randint(0, 255)
				B = random.randint(0, 255)
				codeDict[k] = "Color: %s %s %s" % (R, G, B)
			f = open("conditions.col", 'w')
			pickle.dump(codeDict, f)
			f.close()
		else:
			f = open("conditions.col", 'r')
			codeDict = pickle.load(f)
			f.close()
			l1 = self.prtDict.keys()
			l2 = codeDict.keys()
			l1.sort()
			l2.sort()

			if l1 != l2:
				print "Keys don't match"
				os.remove("conditions.col")
				codeDict = {}
				for k in self.prtDict.keys():
					R = random.randint(0, 255)
					G = random.randint(0, 255)
					B = random.randint(0, 255)
					codeDict[k] = "Color: %s %s %s" % (R, G, B)
				f = open("conditions.col", 'w')
				pickle.dump(codeDict, f)
				f.close()

		self.codeDict = codeDict

	def makePRT(self):
		prtDict = self.prtDict

		keys = prtDict.keys()
		keys.sort()

		prtString = "NrOfConditions:   %i\n\n" % len(keys)


		for k in keys:
			values = prtDict[k]
			prtString = "%s%s\n%i\n\n" % (prtString, k, len(values))
			if values:
				for v in values:
					prtString = "%s%s\n" % (prtString, v)
				prtString = "%s\n%s\n\n" % (prtString, self.codeDict[k])
			else:
				prtString = "%s%s\n\n" % (prtString, self.codeDict[k])       

		self.prtString = prtString

	def makeICA(self):
		f = open("ICA.txt", 'a')
		info = self.info
		

		name = "P%s_%s_%s" % (info['Subject'], info['Experiment'], info['Session'])

		f.write("%" + name + "\n\n")

		keys = self.prtDict.keys()
		keys.sort()

		for k in keys:
			f.write("%s = [" % k)
			values = self.prtDict[k]
			if values:
				for v in values:
					onset = v.split(' ')[0]
					f.write("%s\n" % onset)
			f.write("];\n")
		f.write("me = 7600;\n\nSave '%s'\n\nclear all\n" % name)			


	def writePRT(self, name):
		fname = "output/%s.prt" % name

		f = open(fname, "w")
		f.write(self.settings)
		f.write(self.prtString)
		f.close()
		self.fileList.append(fname)


	def writeEV(self, name=""):
		#make a custom (3-column) EV file for FSL
		prtDict = self.prtDict

		keys = prtDict.keys()
		keys.sort()
		
		for k in keys:

			if name:
				fname = "%s_%s" % (self.fname, name)

			fname = "evs/%s_%s.txt" % (fname, k)

			f = open(fname, "w")

			values = prtDict[k]

			if values:
				for v in values:
					onset = v.split(' ')[0]
					onset = (int(onset) / 1000.)
					f.write("%s %s 1\n" % (onset, self.duration))		
			f.close()
			

		print "%s created succesfully" % fname


