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
import common
import plot

@lg_authority.groups('auth')
class visualize(object):

	@cherrypy.expose
	def index(self, **kwargs):

		cookie = cherrypy.request.cookie

		u = cherrypy.user.name

		#select any tables
		if kwargs.has_key('select'):
			table = kwargs['select']
			print "selecting %s" % table
			common.setCookie('datamaster_table', table)
			select_table = self.table_choice(table, kwargs)
			make_scatter = self.makeScatter(table)

		else:
			table = common.getCookie('datamaster_table')

			if table:
				make_scatter = self.makeScatter(table)
			else:
				make_scatter = no_table

			select_table = self.table_choice(table, kwargs)

		output = ""

		if kwargs:
			if len(kwargs.keys()) > 1:
				output += self.scatter(table, kwargs)

		items = [['select table', select_table], ['scatter', make_scatter]]

		accordion = getAccordion(items, contentID='manage-small')

		output += getPage(accordion, "visualize", "visualize")

		return output

	def table_choice(self, table, kwargs):
		"""choose table interface
		"""

		u = cherrypy.user.name
		posts = mt.MongoAdmin("datamaster").db["tables"].posts
		p = mt.MongoAdmin("datamaster").db["user_tables"].posts

		radios = []
		count = 0
		check = 0

		for row in p.find({'user':u}):
			count += 1
			if table == row['table']:
				check = count

			radios.append(row['table'])

		form = getRadios(radios, 'select', check)

		select_table = getForm(form, visualize_url, legend = 'Select the table that you want to work with')

		return select_table

	def makeScatter(self, table):
		"""scatter plot interface
		"""
		
		tableName = "%s_%s" % (table, cherrypy.user.name)

		posts = mt.MongoAdmin("datamaster").db[tableName].posts

		var_posts = mt.MongoAdmin("datamaster").db["%s_vars" % tableName].posts

		sid, trial, IVs, DVs, sids, run = common.getVariables(tableName)

		output = "<p>Make a scatter plot</p>"
		
		
		output += "<p>Which variables do you want to look at?</p>"
		form = "<label>X Axis:</label>" + getOptions(DVs + IVs, ID="scatter_DV1")
		form += "<label>Y Axis:</label>" + getOptions(DVs + IVs, ID="scatter_DV2")
		form += "<label>Group by <em>(optional)</em>:</label>" + getOptions([''] + IVs + DVs, ID="scatter_IV")


		return output + getForm(form, visualize_url)

	def scatter(self, table, kwargs):
		datatable = "%s_%s" % (table, cherrypy.user.name)
		print kwargs			

		s = plot.scatter("datamaster", datatable, DV=[kwargs['op-scatter_DV1'], kwargs['op-scatter_DV2']], IV=str(kwargs['op-scatter_IV']), fmt='slide', condition={'outlier' : 0})
		s.draw()

		output = ""
		
		output = getAlert("Your scatter plot is ready.  <a href='%s/%s'>Click here to view.</a>" % (domain, s.path), "good")
		common.activity_log("visualize", "scatter", table, kwargs)


		return output
	


if __name__ == '__main__':
#Turn on lg_authority for our website
	cherrypy.config.update(cherry_settings)
	cherrypy.config.update({'server.socket_port':visualize_port,})
	cherrypy.quickstart(visualize())

