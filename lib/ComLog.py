"""Comoonics Logging module

here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComLog.py,v 1.5 2006-06-23 11:50:10 mark Exp $
#

__version__ = "$Revision: 1.5 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/Attic/ComLog.py,v $

import logging
import exceptions

logging.basicConfig()
__default_log=logging.getLogger("")
__default_log.setLevel(logging.DEBUG)
 
#try:
#    logging.basicConfig(level=logging.DEBUG)
#except Exception:
#    logging.basicConfig()

     
def getLogger(name=""):
    
    return __default_log


# $Log: ComLog.py,v $
# Revision 1.5  2006-06-23 11:50:10  mark
# moved log to bottom
#
# Revision 1.4  2006/06/23 07:56:47  mark
# added comaptibility to Python 2.3
#
# Revision 1.3  2006/06/14 10:51:34  mark
# added Log Tag
#
