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
from mako_defs import *

TABLE_VARS = ['subject', 'trial', 'IV', 'DV', 'sids', 'run', 'outlier']

def checkVariables(table, neededVars):

	variables = getVariables(table)
	message = "<p>Sorry m'lord, but you need to select %s in order to use this function.</p><p><a href='%s'>Go to the manage page</a>  to do this.</p>" % ('%s', manage_url)
	output = ""
	indeces = []

	for needed in neededVars:
		index = TABLE_VARS.index(needed)
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
	output = [False] * len(TABLE_VARS)

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

	outlier = VARs.find_one({'var_type': 'outlier'})
	if outlier:
		output[6] = outlier['name']

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

def preview(table, kwargs, source):
	dm = mt.MongoAdmin("datamaster")

	sid, trial, IVs, DVs, sids, run, outlier = getVariables(table, sids=True)

	output = ""

	print sid, trial, IVs, DVs

	if sid and trial and (IVs or DVs):
		if kwargs.has_key('op-preview'):
			sub = kwargs['op-preview']
			try:
				sub = int(sub)
			except:
				pass
		else:
			sub = sids[0]

		if run:
			sort = [run, trial]
			headers = [sid, trial, run] + IVs + DVs
		else:
			headers = [sid, trial] + IVs + DVs
			sort = trial

		if outlier:
			headers += [outlier]

		lines = dm.write(table, {sid:sub}, headers = headers, sort=sort, output="list")
		table = getTable(lines, 'Subject %s' % sub)
		output += "<p>If you just modified your data you might need to <a class='btn' href=%s>refresh the preview</a> to see the changes you just made.</p>" % modify_url
		output += "<p>or switch the participant to:</p>" 
		output += getForm(getOptions(sids, ID="preview", active=sub), form_action=source)
		output += table
	else:
		output += "<p>You do not have all the necessary variables selected.  Better <a class='btn' href='%s'>choose some variables</a>, m'lord.</p>" % manage_url

	return output


def outlierReport(posts, outlier = "outlier"):
	output = "<div class='table'><table><h3>Current outliers</h3><tr><th>Type of outlier</th><th>Count</th><th>% Total</th></tr>"
	total = posts.find().count()
	counts = ""

	for ol in posts.distinct(outlier):
		if ol != 0:
			counts = ""
			counts += "<tr>"
			c = posts.find({outlier : ol}).count()
			if "_zscore>" in ol:
				ol = "%s with z score > %s" % (ol.split('_')[0], ol.split('>')[-1])
			counts += "<td>%s</td><td>%s</td><td>%0.2f%%</td> " % (ol, c, float(c)/float(total) * 100.) 
		output += counts
		output += "</tr>"

	if not counts:
		output = "<p>No outliers labelled yet.</p>"
	else:
		output += "</table></div>"
	
	output += "<hr>"

	return output

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

