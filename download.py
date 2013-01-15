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

@lg_authority.groups('auth')
class download(object):

	@cherrypy.expose
	def index(self, **kwargs):
		u = cherrypy.user.name
		up = mt.MongoAdmin("datamaster").db["user_files"].posts
		cookie = cherrypy.request.cookie
	
		output = ""

		aggregate = ""

		if cookie.has_key("datamaster_table"):
			table = cookie["datamaster_table"].value
			tableName = "%s_%s_vars" % (table, cherrypy.user.name)
			posts = mt.MongoAdmin("datamaster").db[tableName].posts

			IVs = posts.find({'var_type': 'IV'}).distinct('name')
			DVs = posts.find({'var_type': 'DV'}).distinct('name')

			if posts.find_one({'var_type':'subject'}):
				aggregate = self.agg(table)
				download_raw = self.raw(table)
			else:
				aggregate = "<p>You need to select a subject variable, <a href='%s'>go to the manage page</a>  to do this.</p>" % manage_url 
				download_raw = "<p>You need to select a subject variable, <a href='%s'>go to the manage page</a>  to do this.</p>" % manage_url

			if kwargs.has_key('dl'):
				if kwargs['dl'] == 'agg':
					output += self.aggregate(table, kwargs)
				else:
					output += self.get_raw(table, kwargs)

		else:
			aggregate = no_table
			download_raw = no_table

		dl = "<p>"
		fcount = 1
		for row in up.find({'user':u}):
			dl += "File %s : <a href='%s/output/%s'>%s</a><br/>" % (fcount, domain, row['fname'], row['fname'])
			fcount+=1
		dl += "</p>"

		

		items = [['aggregate', aggregate], ['download raw files', download_raw], ["download existing file", dl]]

		output += getAccordion(items, contentID='download-small')

		return getPage(output, "download", "download")


	def agg(self, table):
		tableName = "%s_%s_vars" % (table, cherrypy.user.name)
		posts = mt.MongoAdmin("datamaster").db[tableName].posts

		output = "<p>Here are the variables you have labelled.  Select the ones you want to combine into your new file.  You will get a single file with each subject's average DV(s) for each IV(s).</p>"

		sid = posts.find_one({'var_type': 'subject'})['name']
		trial = posts.find_one({'var_type': 'trial'})['name']

		IVs = posts.find({'var_type': 'IV'}).distinct('name')
		DVs = posts.find({'var_type': 'DV'}).distinct('name')

		form = ""

		form += getCheckbox(IVs)
		form += getCheckbox(DVs)

		form += getCondition(IVs + DVs, 'Include only data where:', ['dl':'agg'])


		output += getForm(form, download_url)

		
		return output


	def aggregate(self, table, kwargs):
		u = cherrypy.user.name
		datatable = "%s_%s" % (table, u)
		tableName = "%s_%s_vars" % (table, u)

		posts = mt.MongoAdmin("datamaster").db[tableName].posts

		sid = posts.find_one({'var_type': 'subject'})['name']
		trial = posts.find_one({'var_type': 'trial'})['name']

		IVs = posts.find({'var_type': 'IV'}).distinct('name')
		DVs = posts.find({'var_type': 'DV'}).distinct('name')

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

		w = mt.WriteTable(dvs, ivs, q, "datamaster", datatable, subject=sid, maxSD=None)

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

		output += "<p>Your data is ready.  <a href='%s/output/%s'>Click here for SPSS format</a> or <a href='%s/output/%s'>click here  for R format.</p>" % (domain, spss_name, domain, r_name)
		return output

	def raw(self, table):
		tableName = "%s_%s_vars" % (table, cherrypy.user.name)
		posts = mt.MongoAdmin("datamaster").db[tableName].posts

		output = "<p>Here are the variables you have labelled.  Select the ones you want to combine into your new files.  You will get one file for each subject you have.</p>"

		sid = posts.find_one({'var_type': 'subject'})['name']
		trial = posts.find_one({'var_type': 'trial'})['name']

		IVs = posts.find({'var_type': 'IV'}).distinct('name')
		DVs = posts.find({'var_type': 'DV'}).distinct('name')

		form = ""

		form += getCheckbox(IVs)
		form += getCheckbox(DVs)

		form += getCondition(IVs + DVs, 'Include only data where:', ['dl','raw'])


		output += getForm(form, download_url)

		return output

	def get_raw(self, table, kwargs):
		u = cherrypy.user.name
		datatable = "%s_%s" % (table, u)
		tableName = "%s_%s_vars" % (table, u)

		dm = mt.MongoAdmin("datamaster")

		posts = mt.MongoAdmin("datamaster").db[tableName].posts

		sid = posts.find_one({'var_type': 'subject'})['name']
		trial = posts.find_one({'var_type': 'trial'})['name']
		IVs = posts.find({'var_type': 'IV'}).distinct('name')
		DVs = posts.find({'var_type': 'DV'}).distinct('name')

		output = ""

		q = parseQuery(kwargs)

		sids = posts.find().distinct(sid)

		for sub in sids:
			dm.write(datatable, dict(q, **{sid:sub}), headers = [sid, trial] + IVs + DVs)

if __name__ == '__main__':
#Turn on lg_authority for our website
	cherrypy.config.update(cherry_settings)
	cherrypy.config.update({'server.socket_port':download_port,})
	cherrypy.quickstart(download())
