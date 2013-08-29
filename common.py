#common.py

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

import mt
import cherrypy
import datetime
from config import *

def checkVariables(table, neededVars):

	variables = getVariables(table)

	table_vars = ['subject', 'trial', 'IV', 'DV', 'sids', 'run'] 	

	message = "<p>Sorry m'lord, but you need to select %s in order to use this function.</p><p><a href='%s'>Go to the manage page</a>  to do this.</p>" % ('%s', manage_url)

	output = ""

	indeces = []
	for needed in neededVars:
		index = table_vars.index(needed)
		if not variables[index]:
			indeces.append(needed)

	for ind in indeces:
		if indeces[-1] == ind and len(indeces) > 1:
			output += " and a <em>%s</em> variable" % ind
		else:
			if len(indeces) > 2:
				output += "a <em>%s</em> variable, " % ind
			else:
				output += "a <em>%s</em> variable" % ind



		
	if output:
		output = message % output

	return output

def getVariables(table, sids=False):
	var_table = "%s_vars" % table

	dm = mt.MongoAdmin("datamaster")
	VARs = mt.MongoAdmin("datamaster").db[var_table].posts
	#order is: sid, trial, IVs, DVs, run 
	output = [False, False, False, False, False, False]

	sid = VARs.find_one({'var_type': 'subject'})
	if sid:
		output[0] = sid['name']

	trial = VARs.find_one({'var_type': 'trial'})
	if trial:
		output[1] = trial['name']

	IVs = VARs.find({'var_type': 'IV'})
	if IVs:
		output[2] = IVs.distinct('name')

	DVs = VARs.find({'var_type': 'DV'})	
	if DVs:
		output[3] = DVs.distinct('name')

	if sid and sids:
		sids = dm.db[table].posts.find().distinct(sid['name'])
		output[4] = sids

	run = VARs.find_one({'var_type': 'run'})
	if run:
		output[5] = run['name']

	return output

def getCookie(name):
	cookie = cherrypy.request.cookie
	cookie = cherrypy.request.cookie
		
	if cookie.has_key(name):
		value = cookie[name].value
		return value
	else:
		return None

def setCookie(name, value):
	cherrypy.response.cookie[name] = value
	cherrypy.response.cookie[name]['path'] = '/'


def removeCookie(name, value):
	cherrypy.response.cookie[name] = value
	cherrypy.response.cookie[name]['path'] = '/'
	cherrypy.response.cookie[name]['expires'] = 0

def activity_log(page, action, table, kwargs={}):
	"""Make an entry into the activity log
	page(string) - one of upload, download, manage, modify
	action(string) - specific function on the page that was used
	table(string) - the table that was acted upon
	kwargs(dict) - kwargs from the page (e.g., the user's parameters)

	"""
	user = cherrypy.user.name
	posts = mt.MongoAdmin("datamaster").getTable('history').posts	
	row = {}
	row['page'] = page
	row['table'] = table
	row['user'] = user
	row['action'] = action
	row['datetime'] = datetime.datetime.utcnow()
	row['kwargs'] = kwargs

	posts.save(row)

