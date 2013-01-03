#file_download.py

import os
import mt
from config import *
import cherrypy
import lg_authority
from mako_defs import *

@lg_authority.groups('auth')
class download(object):
	"""CherryPy server root"""

	auth = lg_authority.AuthRoot()
	auth__doc = "The object that serves authentication pages"

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
			else:
				aggregate = "<p>You need to select a subject variable, <a href='%s'>go to the manage page</a>  to do this.</p>" % manage_url 
			if kwargs:
				output += self.aggregate(table, kwargs)
		else:
			aggregate = no_table

		dl = "<p>"
		fcount = 1
		for row in up.find({'user':u}):
			dl += "File %s : <a href='http://christianbattista.com/output/%s'>%s</a><br/>" % (fcount, row['fname'], row['fname'])
			fcount+=1
		dl += "</p>"

		items = [['make new file', aggregate], ["download existing file", dl]]

		output += getAccordion(items)

		return getPage(output, "Download")


	def agg(self, table):
		tableName = "%s_%s_vars" % (table, cherrypy.user.name)
		posts = mt.MongoAdmin("datamaster").db[tableName].posts

		output = "<p>Here are the variables you have labelled.  Select the ones you want to combine into your new file.</p>"

		sid = posts.find_one({'var_type': 'subject'})['name']
		trial = posts.find_one({'var_type': 'trial'})['name']

		IVs = posts.find({'var_type': 'IV'}).distinct('name')
		DVs = posts.find({'var_type': 'DV'}).distinct('name')

		form = ""

		form += getCheckbox(IVs)
		form += getCheckbox(DVs)

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

		#measures, groupBy, condition, dbName, table
		w = mt.WriteTable(dvs, ivs, {}, "datamaster", datatable, subject=sid, maxSD=None)

		w.Compute()
		w.WriteForSPSS()

		fname = w.name + ".csv"

		up = mt.MongoAdmin("datamaster").db["user_files"].posts

		if not up.find_one({'user':u, 'fname':fname}):
			up.insert({'user':u, 'fname':fname})

		output += "<p>Your data is ready.  <a href='http://www.christianbattista.com/output/%s'>Click to download</a>.</p>" % (fname)
		return output

if __name__ == '__main__':
#Turn on lg_authority for our website
	cherrypy.config.update(cherry_settings)
	cherrypy.config.update({'server.socket_port':download_port,})
	cherrypy.quickstart(download())