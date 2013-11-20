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

#file_download.py

import os
import mt
from config import *
import cherrypy
import lg_authority
from mako_defs import *
from client import *
import zipfile
import common
import makePRTs

@lg_authority.groups('auth')
class download(object):

	@cherrypy.expose
	def index(self, **kwargs):
		u = cherrypy.user.name
		up = mt.MongoAdmin("datamaster").db["user_files"].posts
	
		output = ""

		aggregate = ""

		table = common.getCookie('datamaster_table')

		#select any tables
		if kwargs.has_key('select_table'):
			table = kwargs['select_table']
			common.setCookie('datamaster_table', table)


		if table:
			tableName = "%s_%s_vars" % (table, cherrypy.user.name)
			posts = mt.MongoAdmin("datamaster").db[tableName].posts

			IVs = posts.find({'var_type': 'IV'}).distinct('name')
			DVs = posts.find({'var_type': 'DV'}).distinct('name')

			#aggregate, download
			datatable = "%s_%s" % (table, cherrypy.user.name)
			agg_out = common.checkVariables(datatable, ['subject', 'trial'])
			if agg_out:
				aggregate = agg_out
				download_raw = agg_out
			else:
				aggregate = self.agg(table)
				download_raw = self.raw(table)

			#make_prts
			prts_out = common.checkVariables(datatable, ['subject', 'trial', 'run'])
			if prts_out:
				make_prts = prts_out
			else:
				make_prts = self.make_prts(table)

			if kwargs.has_key('dl'):
				if kwargs['dl'] == 'agg':
					output += self.aggregate(table, kwargs)
				else:
					output += self.get_raw(table, kwargs)
			elif kwargs.has_key('prt_onset'):
				output += self.prts(table, kwargs)


		else:
			aggregate = no_table
			download_raw = no_table
			make_prts = no_table
			

		dl = "<p>"
		fcount = 1
		for row in up.find({'user':u}):
			dl += "File %s : <a href='%s/output/%s'>%s</a><br/>" % (fcount, domain, row['fname'], row['fname'])
			fcount+=1
		dl += "</p>"

		

		items = [['select table', select_table(download_url, table)], ['aggregate', aggregate], ['create single subject files', download_raw], ['make PRTs', make_prts], ['download existing file', dl]]

		output += getAccordion(items, contentID='download-small')

		return getPage(output, "download", "download")


	def agg(self, table):
		"""aggregate interface
		table(string)
		"""
		datatable = "%s_%s" % (table, cherrypy.user.name)
		sid, trial, IVs, DVs, sids, run, outlier = common.getVariables(datatable, sids=False)

		check_vars = common.checkVariables(datatable, ['subject', 'trial', 'IV', 'DV'])

		if check_vars:
			output = check_vars
		else:
			form = ""
			form += getCheckbox(IVs)
			form += getCheckbox(DVs)
			form += getCondition(IVs + DVs + [trial], 'Include only data where:')

			output = "<p>Here are the variables you have labelled.  Select the ones you want to combine into your new file.  You will get a single file with each subject's average DV(s) for each IV(s).</p>"
			output += getForm(form, download_url, hidden=['dl', 'agg'])

		return output

	def aggregate(self, table, kwargs):
		u = cherrypy.user.name
		datatable = "%s_%s" % (table, u)
		sid, trial, IVs, DVs, sids, run, outlier = common.getVariables(datatable, sids=False)

		output = ""

		ivs = []
		dvs = []
		
		for k in kwargs.keys():
			if kwargs[k] == 'on':
				if k in IVs:
					ivs.append(k)
				elif k in DVs:
					dvs.append(k)

		q = parseQuery(kwargs)

		w = mt.WriteTable(dvs, ivs, q, "datamaster", datatable, subject=sid)

		w.Compute()
		w.WriteForSPSS()
		w.WriteForR()

		spss_name = w.name + ".csv"
		r_name = w.name + ".dat"

		up = mt.MongoAdmin("datamaster").db["user_files"].posts

		if not up.find_one({'user':u, 'fname':spss_name}):
			up.insert({'user':u, 'fname':spss_name})

		if not up.find_one({'user':u, 'fname':r_name}):
			up.insert({'user':u, 'fname':r_name})

		common.activity_log("download", "aggregate", table, kwargs)

		output += "<p>Your data is ready.  <a href='%s/output/%s'>Click here for SPSS format</a> or <a href='%s/output/%s'>click here  for R format.</p>" % (domain, spss_name, domain, r_name)
		return output

	def make_prts(self, table):
		"""make prt interface
		"""
		datatable = "%s_%s" % (table, cherrypy.user.name)
		
		sid, trial, IVs, DVs, sids, run, outlier = common.getVariables(datatable, sids=False)
		
		output = "<p>Let's make some PRTs (files for BrainVoyager).</p>"

		form = "<label>Experiment Onset Delay (ms):</label>"
		form += "<input type=\"number\" name=\"prt_onset\" value=0>"
		form += "<label>Stimulus Onset:</label>" + getOptions(IVs, ID="prt_stim_onset")
		form += "<label>Stimulus Offset (ms):</label><input type=\"number\" name=\"prt_offset\" value=2000>"
		form += "<hr>"
		form += "<label>Condition:</label>" + getOptions(IVs, ID="prt_cond")
		form += "<hr>"
		form += "<label>Check Accuracy?</label>" + getRadios(["yes", "no"], name='check_error')
		form += "<label>Accuracy listed in...</label>" + getOptions(DVs, ID="prt_ACC")
		form += "<label>Reaction time listed in...:</label>" + getOptions(DVs, ID="prt_RT")
		form += "<hr>"

		output += getForm(form, download_url)

		return output

	def prts(self, table, kwargs):
		"""make prts function
		"""
		datatable = "%s_%s" % (table, cherrypy.user.name)
		sid, trial, IVs, DVs, sids, run, outlier = common.getVariables(datatable, sids=False)

		#get the values
		onset_start = int(kwargs['prt_onset'])
		stim_onset = kwargs['op-prt_stim_onset']
		stim_offset = int(kwargs['prt_offset'])
		if kwargs['check_error'] == 'no':
			check_errors = False
		else:
			check_errors = True
		ACC = kwargs['op-prt_ACC']
		RT = kwargs['op-prt_RT']

		myCond = kwargs['op-prt_cond']

		settings = settings = """FileVersion:       2\n\nResolutionOfTime:   msec\n\nExperiment:         %s\n\nBackgroundColor:    0 0 0\nTextColor:          255 255 255\nTimeCourseColor:    255 255 255\nTimeCourseThick:    3\nReferenceFuncColor: 0 0 80\nReferenceFuncThick: 3\n\n""" % (table)

		prt_maker = makePRTs.prtFile(datatable, sid, run,  settings, onset_start, stim_offset, check_errors, source="database")

		prt_maker.make(myCond, [], stim_onset, ACC, RT, trial, balance=False)

		files = prt_maker.fileList
		zipname = "%s_%s_prts" % (datatable, myCond)
		zippath = os.path.join("output", "%s.zip" % zipname)
		z = zipfile.ZipFile(zippath, "w")
		for f in files:
			z.write(f)
			os.system('rm %s' % f)

		z.close()

		up = mt.MongoAdmin("datamaster").db["user_files"].posts

		if not up.find_one({'user':cherrypy.user.name, 'fname':zipname + ".zip"}):
			up.insert({'user':cherrypy.user.name, 'fname':zipname + ".zip"})

		common.activity_log("download", "download prts", table, kwargs)

		output = getAlert("Your files are ready.  <a href='%s/%s'>Click here to download.</a>" % (domain, zippath), "good")

		return output

	def raw(self, table):
		"""Raw data interface
		table(string)
		"""
		datatable = "%s_%s" % (table, cherrypy.user.name)
		sid, trial, IVs, DVs, sids, run, outlier = common.getVariables(datatable, sids=False)

		form = ""
		form += getCondition([trial] + IVs + DVs, 'Include only data where:')

		output = "<p>You will get one file for each subject you have.</p>"
		output += getForm(form, download_url, hidden=['dl','raw'])

		return output

	def get_raw(self, table, kwargs):
		"""Print the raw data (csv format) and put data in a zip file for download
		table(string) - name of table to pull the vars from
		kwargs - optional query info
		"""
		u = cherrypy.user.name
		datatable = "%s_%s" % (table, u)
		dm = mt.MongoAdmin("datamaster")
		sid, trial, IVs, DVs, sids, run, outlier = common.getVariables(datatable, sids=True)

		q = parseQuery(kwargs)
		files = []

		for sub in sids:
			headers = [sid, trial] + IVs + DVs
			sort = trial
			if run:
				headers.insert(3, run)
				sort = [run, trial]
			if outlier:
				headers += [outlier]
			name = dm.write(datatable, dict(q, **{sid:sub}), headers = headers, sort=sort)
			files.append(name)

		zipname = datatable
		zipname = os.path.join("output", zipname + ".zip")
		z = zipfile.ZipFile(zipname, 'w')
			
		for f in files:
			z.write(f + ".csv")
			os.system('rm %s.csv' % f)

		z.close()

		up = mt.MongoAdmin("datamaster").db["user_files"].posts

		if not up.find_one({'user':u, 'fname':datatable + ".zip"}):
			up.insert({'user':u, 'fname':datatable + ".zip"})

		common.activity_log("download", "download raw", table, kwargs)

		output = getAlert("Your files are ready.  <a href='%s/%s'>Click here to download.</a>" % (domain, zipname), "good")

		return output

if __name__ == '__main__':
#Turn on lg_authority for our website
	cherrypy.config.update(cherry_settings)
	cherrypy.config.update({'server.socket_port':download_port,})
	cherrypy.quickstart(download())
