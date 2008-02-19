""" Comoonics path modificationset module
This module execute all given modifications with the given path as current working directory

Example Configuration:
    <modificationset type="isofs" name="/mnt/myiso.iso">
        <path name="/tmp/isofs"/>
        <path name="/tmp/extras"/>
        <properties>
            <property name="bootcd" value="livecd">
            <property name="cdlabel" value="COMOONICS_LIVECD"/>
        </properties>
    </modificationset>
"""

# here is some internal information
# $Id: ComISOFSModificationset.py,v 1.1 2008-02-19 17:32:20 mark Exp $
#


__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComISOFSModificationset.py,v $

from ComModificationset import ModificationsetJournaled
from comoonics import ComLog, ComSystem
from comoonics.ComPath import Path
from comoonics.ComExceptions import ComException

import os
import os.path
from xml import xpath

CMD_MKISOFS="/usr/bin/mkisofs"

class ISOFSModificationset(ModificationsetJournaled):
    """ implementation class for this modificationset """
    __logStrLevel__="comoonics.enterprisecopy.ComISOFSModificationset.ISOFSModificationset"
    logger=ComLog.getLogger(__logStrLevel__)

    def __init__(self, element, doc):
        """
        default constructor:
        __init__(element, doc)
        """
        super(ISOFSModificationset, self).__init__(element, doc)
        try:
            __path=xpath.Evaluate('path', element)
        except Exception:
            raise ComException("Path for modificationset \"%s\" not defined" %self.getAttribute("name", "unknown"))
        self.pathlist=__path
        self.createModificationsList(self.getElement().getElementsByTagName("modification"), doc)
        self.isoname=self.getAttribute("name")
 
    def doPre(self):
        ISOFSModificationset.logger.debug("doPre() CWD: " + os.getcwd())
        super(ISOFSModificationset, self).doPre()

    def doPost(self):
        super(ISOFSModificationset, self).doPost()
        self.replayJournal()
        self.commitJournal()
        ISOFSModificationset.logger.debug("doPost() CWD: " + os.getcwd())
        __cmd=self._get_mkisofs_command()
        __rc, __ret = ComSystem.execLocalStatusOutput(__cmd)
        ISOFSModificationset.logger.debug("mkisofs: "  + __cmd + ": " + __ret)
        if __rc != 0:
            raise ComException(__cmd + __ret)


    def _get_mkisofs_command(self):
        cmd=CMD_MKISOFS + " -o " + self.isoname + " -J -R -D "
        if self.getProperties() and self.getProperties().has_key("bootcd"):
            if self.getProperties().getProperty("bootcd").getValue() == "livecd": 
                cmd = cmd + "-no-emul-boot -boot-info-table -boot-load-size 4 -b boot/isolinux.bin -c boot/isolinux.boot "
        if self.getProperties() and self.getProperties().has_key("cdlabel"):
            key=self.getProperties().getProperty("cdlabel")
            cmd = cmd + "-A '" + key.getValue() + "' -V '" + key.getValue() + "'"
        for element in self.pathlist:
            cmd = cmd + " " + element.getAttribute("name")
 
        
        return cmd

# $Log: ComISOFSModificationset.py,v $
# Revision 1.1  2008-02-19 17:32:20  mark
# initial check in
#
# 
#
