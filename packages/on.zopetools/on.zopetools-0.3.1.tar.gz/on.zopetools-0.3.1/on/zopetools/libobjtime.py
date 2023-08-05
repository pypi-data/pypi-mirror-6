
### Setting the time on Plone objects
#
# Slow! If you want to set the time on many objects,
# grab the idea and tune by hand.

"""
Original function body (thanks, Moo-_-):
obj.setCreationDate(dt)
od = obj.__dict__
od['notifyModified'] = lambda *args: None
obj.reindexObject()
del od['notifyModified']
"""


import logging

tlogger = logging.getLogger('libobjtime:')

def reindexObj(obj): #, dt, f):
    """Set the appropriate date and time of an object, given by 'f'.

       Prevent update of modification date during reindexing.
    """
    global tlogger

    od = obj.__dict__
    od['notifyModified'] = lambda *args: None
    obj.reindexObject()
    del od['notifyModified']
    

def setObjCDate(obj, dt):
    """Set the creation date."""
    obj.setCreationDate(dt)
    reindexObj(obj)


def setObjEDate(obj, dt):
    """Set the effective date."""
    obj.setEffectiveDate(dt)
    reindexObj(obj)


def setObjMDate(obj, dt):
    """Set the modification date."""
    obj.setModificationDate(dt)
    reindexObj(obj)


def setObjXDate(obj, dt):
    """Set the expiration date."""
    obj.setExpirationDate(dt)
    reindexObj(obj)


