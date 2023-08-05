### copyright (c) 2012-2014 Toni Mueller <support@oeko.net>
### AGPLv3 if possible, otherwise GPLv3 or later
### incorporates portions of code from ore.contentmirror

import os
import sys
import transaction
import logging

# Zope2 stuff ahead:
from App.config import getConfiguration
from AccessControl.SecurityManagement import newSecurityManager

from AccessControl.User import system
from AccessControl import Unauthorized

from Products.ZODBMountPoint.MountedObject import manage_addMounts

# get the 'app' object:

def get_app():
    frame = sys._getframe(2)
    return frame.f_locals.get('app')


def checkForFolder(app, path):
    """Do we have the folder?"""
    try:
        place = app.unrestrictedTraverse(path)
        return place.isPrincipiaFolderish == 1
    except:
        return False


def createMountPointsIfRequired(app):
    """The ZODB mount points may not exist. We need to create them."""
    reserved = ('main', 'temporary')
    dbmgr = app['Control_Panel']['Database']
    dbtab = getConfiguration().dbtab
    dbs = [db for db in dbmgr.getDatabaseNames() if not db in reserved]
    dbpaths = dbtab.listMountPaths()
    allpaths = [mp[0] for mp in dbpaths if mp[1] in dbs]
    # ZODB mount points can only be created by the 'system' user:
    newSecurityManager(None, system)
    transaction.commit()
    for path in allpaths:
        try:
            manage_addMounts(app, (path, ))
        except:
            print " failed."
            pass                          # it probably already exists
    admin = app.acl_users.getUserById("admin")
    newSecurityManager(None, admin)
    transaction.commit()


def main(app=None):
    if app is None:
        print "'app' object was None!"
        app = get_app()
    createMountPointsIfRequired(app)


if "app" in locals():
    main(app)
