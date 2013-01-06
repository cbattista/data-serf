import os
import mt

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

