#user.py

import cherrypy
import lg_authority

#Restrict default access to logged in users
@lg_authority.groups('auth')
class Root(object):
    """CherryPy server root"""

    auth = lg_authority.AuthRoot()
    auth__doc = "The object that serves authentication pages"

    #Allow everyone to see the index page
    @cherrypy.expose
    @lg_authority.groups('any')
    def index(self):
        return '<p>Welcome!</p><p>Would you like to <a href="protected">view protected information?</a></p>'

    #This method inherits restricted access from the Root class it belongs to
    @cherrypy.expose
    def protected(self):
        return '<p>Welcome, {user}!</p><p><a href="auth/logout">Logout</a> and try again?<p>'.format(user=cherrypy.user.name)

#Turn on lg_authority for our website
cherrypy.config.update({
    'tools.lg_authority.on': True
    })

cherrypy.config.update({'tools.lg_authority.site_registration':'open'})
cherrypy.config.update({'tools.lg_authority.site_storage' : 'pymongo', 'tools.lg_authority.site_storage_conf': {'db': 'datamaster_users'}})


#Run the webserver
cherrypy.config.update({'server.socket_port':8585,})
cherrypy.quickstart(Root())
