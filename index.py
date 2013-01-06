import os
import mt

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

import cherrypy
from mako_defs import *
from config import *
import lg_authority

class index(object):

	auth = lg_authority.AuthRoot()
	auth__doc = "The object that serves authentication pages"


	@cherrypy.expose
	def index(self):
		output = ""

		output += getIndexContent()

		output = getPage(output, '')

		return output 


if __name__ == '__main__':

	cherrypy.config.update({'server.socket_port':index_port})
	cherrypy.config.update(cherry_settings)
	cherrypy.quickstart(index())

