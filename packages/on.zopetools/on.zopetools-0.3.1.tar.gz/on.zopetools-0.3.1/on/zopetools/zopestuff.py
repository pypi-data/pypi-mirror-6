### copyright (c) 2012-2014 Toni Mueller <support@oeko.net>
### AGPLv3 if possible, otherwise GPLv3 or later
### incorporates portions of code from ore.contentmirror

import os
import sys
import optparse
import transaction
import logging

# Zope2 stuff ahead:
from App.config import getConfiguration
from AccessControl.SecurityManagement import newSecurityManager

from AccessControl.User import system
from AccessControl import getSecurityManager
from AccessControl import Unauthorized

#from OFS.Folder import Folder
#from OFS.Folder import manage_addFolder
from Products.ZODBMountPoint.MountedObject import manage_addMounts

# ZCA stuff:
from zope.component.interfaces import  ISite

# Plone stuff:
from Products.CMFPlone.factory import addPloneSite
from Products.CMFPlone.factory import _DEFAULT_PROFILE
from Products.CMFCore.utils import getToolByName

try:  # recent Plones:
    from zope.component.hooks import setSite
except:
    from zope.app.component.hooks import setSite


### Some global objects to work with:

site = None                             # the site we are working on
catalog = None


# get the 'app' object:

def get_app():
    frame = sys._getframe(2)
    return frame.f_locals.get('app')


def setup_parser():
    parser = optparse.OptionParser(
        usage="Usage: ./bin/managezope ./bin/%prog [options] portal_path")
    parser.add_option(
        '-k', '--kill', dest="kill", default=False, action='store_true',
        help="Delete and re-create the Plone site before importing")
    parser.add_option(
        '-l', '--load', dest="load", default=False, action='store_true',
        help="Run the importer step, instead of only creating the Plone site.")
    parser.add_option(
        '-p', '--product', dest="products", default="",
        help="import product into the Plone site")
    parser.add_option(
        '-q', '--quiet', dest='verbose', action='store_false',
        help="quiet/silent output (currently a NOP)", default=True)
    parser.add_option(
        '-d', '--db', dest='database', default="",
        help="use the specified database uri (currently a NOP)")
    return parser


def checkForFolder(app, path):
    """Do we have the folder?"""
    print "checkForFolder()"
    try:
        place = app.unrestrictedTraverse(path)
        return place.isPrincipiaFolderish == 1
    except:
        return False
        

def genPloneSite(app, container, name='Plone'):
    """Create a Plone site in the given container."""
    print("genPloneSite(), container = ", container)
    admin=app.acl_users.getUserById("admin")
    newSecurityManager(None, admin)
    transaction.commit()
    print("genPloneSite() admin = ", repr(admin))
    ploneSite = addPloneSite(container, name,
                             description=u'My New Plone Site') #,
                             #email_from_address='info@oeko.net',
                             #extension_ids=('plonetheme.classic:default',
                             #               'plonetheme.sunburst:default'),
                             #setup_content=False
                             #)
    """ , title=name,
                             setup_content = True,
                             profile_id =_DEFAULT_PROFILE,
                             extension_ids = ('plonetheme.classic:default','plonetheme.sunburst:default'),
                             default_language = 'en',
                             )
    """
    transaction.savepoint()
    return ploneSite


def delPloneSite(app, instance_path):
    """Delete the Plone site in the given container and pack the
       respective database, in order to conserve space.
    """
    print "delPloneSite(): instance_path = ", instance_path
    container, site = getSiteContainerPath(app, instance_path)
    try:
	#container.manage_delObjects([site,])
        # "Fail safe deleting":
	container._delObject(site, suppress_events=True)
    except:
        print "Could not delete site %s, but continuing anyway." % str(site)
    ### As seen from the shell:
    # >>> dbtab = getConfiguration().dbtab
    # >>> dbpaths = dbtab.listMountPaths()
    # >>> dbpaths
    # [('/temp_folder', 'temporary'), ('/02/mnt', '02'), ('/04/mnt', '04'), ('/', 'main'), ('/01/mnt', '01'), ('/03/mnt', '03')]
    dbs = app['Control_Panel']['Database']
    dbnames = dbs.getDatabaseNames()
    print "delPloneSite(%s): container = %s, dbs = %s" % \
          (str(instance_path), str(container), str(dbnames))
    dbname = instance_path
    print "dbname: ", dbname
    if dbname.startswith('/'):
        dbname = dbname[1:]
    if '/' in dbname:
        dbname = dbname[:dbname.find('/')]
    #print "  folder (before mangling): ", dbname
    # not in a ZODB mount point:
    print "  folder (after mangling): ", dbname
    if dbname not in dbnames:
        dbname = 'main'
    print "  database name to pack: ", dbname
    dbs[dbname].manage_pack()
    transaction.savepoint()


def getSiteContainerPath(app, instance_path):
    """Return the container of the new site, or throw an exception.
       The site may or may not exist, but the container for it has
       to exist.
    """
    print "genSiteContainerPath(): instance_path = ", instance_path
    if app is None:
        app = get_app()
    container = app

    print "getSiteContainerPath(%s, %s)" % (str(app), str(instance_path))
    elements = instance_path.split('/')
    print "elements: ", elements
    sitename = elements.pop()
    print "sitename: ", sitename
    if elements[0] == '' and len(elements) > 0:
        elements = elements[1:]
    container = app
    while len(elements) > 0:
        print "sitename: %s, elements: %s" % (sitename, str(elements))
        component = elements.pop(0)
        container = container[component]
    #component = elements.pop(0)
    print "return values: site=%s, sitename=%s" % (str(container), str(sitename))
    return container, sitename


def recreateSite(app, instance_path):
    """Create a new Plone site at instance_path, possibly deleting
       a Plone site at that location.
    """
    print "recreateSite(%s, %s)" % (str(app), str(instance_path))
    # check whether the path to the site exists:
    #try:
        # now site points to the container for the Plone site
    container, site = getSiteContainerPath(app, instance_path)
    #except:
    #    container, site = None, None
    #    return None, None

    dbs = app['Control_Panel']['Database']
    dbnames = dbs.getDatabaseNames()

    print "container = %s, site = %s" % (container, site)
    #print "recreateSite(): dbnames = %s" % str(dbnames)
    #print "container = %s, site = %s" % (str(container), str(site))
    if site in container.keys():
        #container.manage_delObjects([site,])
        delPloneSite(app, instance_path)
    # now: do some ZODB packing
    genPloneSite(app, container, site)


def createMountPointsIfRequired(app):
    """The ZODB mount points may not exist. We need to create them."""
    # print "container: %s, site: %s (instance path %s)" % (container, site, instance_path)
    print "createMountPointsIfRequired(%s)" % str(app)
    reserved = ('main', 'temporary')
    dbmgr = app['Control_Panel']['Database']
    dbtab = getConfiguration().dbtab
    dbs = [db for db in dbmgr.getDatabaseNames() if not db in reserved]
    dbpaths = dbtab.listMountPaths()
    allpaths = [mp[0] for mp in dbpaths if mp[1] in dbs]
    # Now that we have all required paths, we can try to create the
    # mount points.
    # First step: Change the privilege level.
    ### can we do without these:
    newSecurityManager(None, system)
    transaction.commit()
    for path in allpaths:
        print "trying to make path ", path
        try:
            manage_addMounts(app, (path, ))
        except:
            print " failed."
            pass                          # it probably already exists
    admin = app.acl_users.getUserById("admin")
    newSecurityManager(None, admin)
    transaction.commit()


def main(app=None, instance_path=None):
    #import pdb; pdb.set_trace()
    print "sys.argv = ", sys.argv
    parser = setup_parser()
    print "parser = ", parser
    if len(sys.argv) > 2 and sys.argv[1] == '-c':
        print "upper branch"
        options, args = parser.parse_args(sys.argv[3:])
    else:
        print "lower branch"
        options, args = parser.parse_args()
    print "options parsed. options = %s, args = %s" % (str(options), str(args))
    global site
    if len(args) != 1:
        parser.print_help()
        sys.exit(1)
        return
    if app is None:
        app = get_app()
    instance_path = args[0]
    createMountPointsIfRequired(app)
    if options.kill:
        recreateSite(app, instance_path)
    portal = app.unrestrictedTraverse(instance_path)
    setSite(portal)
    site = portal

    print "working in ", os.getcwd()
    print "importing into site %s" % str(portal)

    products = []
    pqi = getToolByName(portal, 'portal_quickinstaller')
    if options.products:
        np = options.products.split()
        for product in np:
            if product not in pqi:
                products.append(product)
    st = getToolByName(portal, "portal_setup")
    print "on.zopetools: products = ", products
    for product in products:
        print "processing ", product
        __import__(product)
        st.runAllImportStepsFromProfile("profile-%s:default" % product)
        if product not in pqi:
            raise TypeError, '%s still not installed - bailing out' % product

    ### Replace this with some kind of transmogrifier stuff for the general case.
    #if options.load:
    #    importEverything(portal)
    transaction.commit()


if "app" in locals():
    main(app)
