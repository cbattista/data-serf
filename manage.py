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
import mt
from config import *
import cherrypy
import lg_authority
from mako_defs import *

@lg_authority.groups('auth')
class manage(object):

	@cherrypy.expose
	def index(self, **kwargs):
		u = cherrypy.user.name
		posts = mt.MongoAdmin("datamaster").db["tables"].posts
		p = mt.MongoAdmin("datamaster").db["user_tables"].posts
		cookie = cherrypy.request.cookie

		review_vars = self.reviewVars(None)

		if kwargs:
			if len(kwargs.keys()) > 1:
				review_vars = self.reviewVars(kwargs)

		if kwargs.has_key('table'):
			table = kwargs['table']
		else:
			if cookie.has_key('datamaster_table'):
				table = cookie["datamaster_table"].value
			else:
				table = None

		form = "<p>Select the table that you want to work with</p>"
		
		radios = []
		count = 0
		check = 0

		for row in p.find({'user':cherrypy.user.name}):
			count += 1
			if table == row['table']:
				check = count

			radios.append(row['table'])

		name = 'table'

		form = getRadios(radios, name, check)

		select_table = getForm(form, manage_url)

		if table:
			choose_vars = self.chooseVars(table)
		else:
			choose_vars = no_table


		items = [['select table', select_table], ['choose variables', choose_vars], ['review variables', review_vars]]

		accordion = getAccordion(items, contentID='manage-small')

		output = getPage(accordion, "manage", "manage")

		return output

	def chooseVars(self, table):
		cherrypy.response.cookie['datamaster_table'] = table

		tableName = "%s_%s" % (table, cherrypy.user.name)

		posts = mt.MongoAdmin("datamaster").db[tableName].posts

		var_posts = mt.MongoAdmin("datamaster").db["%s_vars" % tableName].posts 

		headers = mt.GetKeys(posts)

		output = "<p>Which variables are you most interested in?  Use the radio buttons to indicate which variables are independent (IV) or dependent (DV).  You also should tell us which variables are the trial and subject info. </p>"""

		output += "<p>table: <em>%s</em><p>" % table

		table_data = []

		for h in headers:
			row = [h]
			for value in ['IV', 'DV', 'subject', 'trial', 'none']:
				inp = "<label class='radio'><input type = 'radio' name = '%s' value = '%s'/>%s</label>" % (h, value, value)
				var = var_posts.find_one({'name':h})
				if var:
					var_type = var['var_type']
					if var_type == value:
						inp = "<label class='radio'><input type = 'radio' name = '%s' value = '%s' checked='checked'/>%s</label>" % (h, value, value)
				row.append(inp)
			table_data.append(row)
		
		table_data = getTable(table_data)

		form = getForm(table_data, manage_url)

		output += form

		return output
	
	def reviewVars(self, kwargs):
		cookie = cherrypy.request.cookie
		if cookie.has_key("datamaster_table"):
	
			table = cookie["datamaster_table"].value
			tableName = "%s_%s_vars" % (table, cherrypy.user.name)
			posts = mt.MongoAdmin("datamaster").db[tableName].posts

			if kwargs:
				for k in kwargs.keys():
					posts.remove({'name':k})
					posts.update({'name':k}, {'$set':{'var_type':kwargs[k]}}, upsert=True)



			sid = posts.find_one({'var_type': 'subject'})
			trial = posts.find_one({'var_type': 'trial'})

			IVs = posts.find({'var_type': 'IV'}).distinct('name')
			DVs = posts.find({'var_type': 'DV'}).distinct('name')

			output = ""

			if sid or trial or IVs or DVs:
				output += "<p>Here are the variables you have labelled:</p>"

				output += "<ul>"
				if sid:
					output += "<li>subject: %s</li>" % sid['name']
				if trial:
					output += "<li>trial: %s</li>" % trial['name']
				if IVs:
					output += "<li>IVs: %s</li>" % prettyList(IVs)
				if DVs:
					output += "<li>DVs: %s</li>" % prettyList(DVs)
				output += "</ul>"
			else:
				output += "<p>You have no variables selected yet.</p>"


		else:
			output = no_table
	
		return output
	


if __name__ == '__main__':
#Turn on lg_authority for our website
	cherrypy.config.update(cherry_settings)
	cherrypy.config.update({'server.socket_port':manage_port,})
	cherrypy.quickstart(manage())

