"""

Comoonics cluster configuration package

Provides modules to manage and query the cluster configuration. Discovers type 
of used cluster configuration by parsing given cluster configuration.
"""

# @(#)$File$
#
# Copyright (c) 2001 ATIX GmbH, 2007 ATIX AG.
# Einsteinstrasse 10, 85716 Unterschleissheim, Germany
# All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
from comoonics.ComDataObject import DataObject
from comoonics.ComExceptions import ComException

__version__='$Revision: 1.11 $'

#__all__=['clusterconf', 'querymapfile', 'clusterdtd', 'RedHatClusterConst', 'OSRClusterConst', 
#         'getClusterInfo', 'ClusterMacNotFoundException', 'ClusterInformationNotFound', 'ClusterIdNotFoundException',
#         'getClusterRepository', 'ClusterObject', 'ClusterRepositoryConverterNotFoundException' ]


class ClusterMacNotFoundException(ComException): pass
class ClusterInformationNotFound(ComException): pass
class ClusterIdNotFoundException(ComException): pass

class ClusterObject(DataObject):
    non_statics=dict()
    def __init__(self, *params, **kwds):
        super(ClusterObject, self).__init__(*params, **kwds)
        self.non_statics=dict()
    def isstatic(self, _property):
        if self.non_statics.has_key(_property):
            return False
        return True
    def addNonStatic(self, name, rest=None):
        path_end=self.non_statics
        path_end[name]=rest
    def query(self, _property, *params, **keys):
        pass
    def __getattr__(self, value):
        if not self.isstatic(value):
            return self.query(value)
        else:
            return DataObject.__getattribute__(self, value)

def getClusterInfo(clusterRepository):
    """
    Factory method to return the fitting instance of the cluster information classes#
    @param clusterRepository: the relevant cluster repository
    @type  clusterRepository: L{comoonics.cluster.ComClusterRepository.ClusterRepository}
    @return:                  the clusterinformation relevant to the clusterRepository
    @rtype:                   L{ClusterRepository} 
    """
    from comoonics.cluster.ComClusterRepository import ClusterRepository
    if isinstance(clusterRepository, ClusterRepository):
        cls = clusterRepository.getClusterInfoClass()
    else:
        raise ClusterInformationNotFound("Could not find cluster information for cluster repository %s." %(clusterRepository))
    return cls(clusterRepository)

class ClusterRepositoryConverterNotFoundException(ComException): pass

def getClusterRepository(*args, **kwds):
    """
    Factory method to autocreate a fitting cluster repository.
    The following call semantics are supported:
    getClusterRepository(filename)
    getClusterRepository(docelement, doc, options)
    Parses the given filename as configuration to the given cluster or already accept a parsed configuration. 
    Right now only xml.dom.Node representation of the cluster configuration is supported.
    @param filename:   representation of the path to the cluster configuration. If it is a xml file it will be parsed. 
                       If not an exception is thrown.
    @type  filename:   L{String} 
    @param docelement: the already parse configuration as dom document.
    @type  docelement: L{xml.dom.Element}
    @param doc:        the document itself.
    @type  doc:        L{xml.dom.Docuement}
    @param options:    options see ClusterRepository constructor.
    @type  options:    L{dict}
    @return:           The best fitting clusterconfiguration repository class instance
    @rtype:            L{ComoonicsClusterRepository}, L{RedHatClusterRepository}, ..
    """
    from comoonics.XmlTools import evaluateXPath
    from comoonics.DictTools import searchDict
    from comoonics.cluster.ComClusterRepository import ClusterRepository, ComoonicsClusterRepository, RedHatClusterRepository
    repositoryclass=ClusterRepository
    if len(args) >= 1 and isinstance(args[0], basestring):
        doc=parseClusterConf(args[0])
        newargs=[doc.documentElement,doc]
        newargs.extend(args[1:])
        args=newargs
        if len(evaluateXPath(ComoonicsClusterRepository.getDefaultComoonicsXPath(), doc.documentElement)) > 0:
            repositoryclass = ComoonicsClusterRepository
        elif len(evaluateXPath(RedHatClusterRepository.getDefaultClusterNodeXPath(), doc.documentElement)) > 0:
            repositoryclass = RedHatClusterRepository
    if len(args) >= 2:
        if (args[0] != None):                
            if evaluateXPath(ComoonicsClusterRepository.getDefaultComoonicsXPath(""), args[0]) or len(args[2]) == 0:
                repositoryclass = ComoonicsClusterRepository
            elif evaluateXPath(RedHatClusterRepository.getDefaultClusterNodeXPath(), args[0]):
                repositoryclass = RedHatClusterRepository
                
        elif type(args[2]) == dict:
            if searchDict(args[2],"osr"):
                repositoryclass = ComoonicsClusterRepository
            elif searchDict(args[2],RedHatClusterRepository.element_clusternode):
                repositoryclass = RedHatClusterRepository
            
    return repositoryclass(*args, **kwds) #, *args, **kwds)
    
# needed files
try:
    clusterconf=os.environ["CLUSTERCONF"]
except:
    clusterconf = "/etc/cluster/cluster.conf"
try:
    querymapfile=os.environ["QUERYMAPFILE"]
except:
    querymapfile="/etc/comoonics/querymap.cfg"

def parseClusterConf(_clusterconf=clusterconf, _validate=False):
    if not _clusterconf:
        _clusterconf=clusterconf
    # parse the document and create comclusterinfo object
    file = os.fdopen(os.open(_clusterconf,os.O_RDONLY))
    doc= parseClusterConfFP(file, _clusterconf, _validate)
    file.close()
    return doc

def parseClusterConfFP(_clusterconffp, _clusterconf, _validate=False):
    from comoonics import ComLog
    from comoonics import XmlTools
    try:
        doc = XmlTools.parseXMLFP(_clusterconffp)
    except Exception, arg:
        ComLog.getLogger().critical("Problem while reading clusterconfiguration (%s): %s" %(_clusterconf, str(arg)))
        raise
    return doc

def setDebug(option, opt, value, parser):
    from comoonics import ComLog
    import logging
    ComLog.setLevel(logging.DEBUG)
#    ComLog.getLogger().propagate=1

def commonoptparseroptions(parser):
    """
    Sets the give optparser to the common options needed by all cdsl commands.
    """
    import logging
    from ComClusterRepository import RedHatClusterRepository
    
    logging.basicConfig()
    
    parser.add_option("-v", "--verbose", action="callback", callback=setDebug, help="Be more chatty. Default is to talk only about important things.")
    parser.add_option("-c", "--clusterconf", dest="clusterconf", default=RedHatClusterRepository.getDefaultClusterConf(), 
                      help="Overwrite cluster configurationfile. Default: %default.")
    return parser

def get_defaultsfiles():
    import os.path
    default_dir = "/etc/comoonics"
    home_dir = os.path.join(os.environ.get('HOME', ''), ".comoonics")
    globalcfgdefault_file= os.path.join(default_dir, "cluster.cfg") 
    localcfgdefault_file= os.path.join(home_dir, "cluster.cfg")
    return globalcfgdefault_file, localcfgdefault_file

def get_defaultsenvkey():
    return "COMOONICS_CLUSTER_CFG" 

from comoonics.cluster.ComQueryMap import QueryMap

###############
# $Log: __init__.py,v $
# Revision 1.11  2010-11-21 21:45:28  marc
# - fixed bug 391
#   - moved to upstream XmlTools implementation
#
# Revision 1.10  2010/02/05 12:13:08  marc
# - take default clusterconf if none given
#
# Revision 1.9  2009/07/22 13:01:58  marc
# ported to getopts
#
# Revision 1.8  2009/07/22 08:37:09  marc
# Fedora compliant
#
# Revision 1.7  2009/05/27 18:31:59  marc
# - prepared and added querymap concept
# - reviewed and changed code to work with unittests and being more modular
#
# Revision 1.6  2009/02/24 10:16:01  marc
# added helper method to parse clusterconfiguration
#