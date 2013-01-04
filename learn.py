import os
import mt

import cherrypy
from mako_defs import *
from config import *
import lg_authority

class learn(object):


	@cherrypy.expose
	def index(self):
		output = ""

		output += getLearnContent()

		output = getPage(output, 'dataserf basics')

		return output 


if __name__ == '__main__':

	cherrypy.config.update({'server.socket_port':learn_port})
	cherrypy.config.update(cherry_settings)
	cherrypy.quickstart(learn())

