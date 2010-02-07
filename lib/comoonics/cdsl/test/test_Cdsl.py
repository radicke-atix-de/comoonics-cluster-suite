'''
Created on Apr 28, 2009

@author: marc
'''
import sys
sys.path.append('/usr/lib/python%s/site-packages/oldxml' % sys.version[:3])
import unittest
import setup

class test_Cdsl(unittest.TestCase):
    def test_A_CdslsCreate(self):
        from comoonics.cdsl import cmpbysubdirs
        from comoonics.cdsl.ComCdsl import Cdsl
        _cdsls=repository.getCdsls()
        _cdsls.sort(cmpbysubdirs)
        for _cdsl in _cdsls:
            print "+ %s\n" %_cdsl
            _cdsl.commit(force=True)
            self.assertTrue(_cdsl.exists(), "%s CDSL %s does not exist!" %(_cdsl.type, _cdsl))

    def test_B_CdslsValidate(self):
        from comoonics.cdsl.ComCdslValidate import CdslValidate
        validate=CdslValidate(repository, setupCluster.clusterinfo)
        _added, _removed=validate.validate(onfilesystem=False, update=False, root=setup.tmppath)
        print "Validate.."
        self.assertTrue(len(_added)==0 and len(_removed)==0, "Cdslsearch didn't succeed. Added %s, Removed %s" %(_added, _removed))
        print "Ok\n"
        _cdsls=repository.getCdsls()
        print "-%s" %_cdsls[-1]
        _removed_cdsl=repository.delete(_cdsls[-1])
        _added, _removed=validate.validate(onfilesystem=True, update=True, root=setup.tmppath)
        self.assertEquals(_added[0].src, _removed_cdsl.src, "The removed cdsl %s is different from the added one %s" %(_added[0].src, _removed_cdsl.src))
        print "+%s" %_added[0].src

    def test_C_CdslSubPaths(self):
        for cdsl in repository.getCdsls():
            print "Subpaths2parent(%s): %s" %(cdsl, cdsl._getSubPathsToParent())

    def test_D_CdslDestPaths(self):
        for cdsl in repository.getCdsls():
            print "destpaths(%s): %s" %(cdsl, cdsl.getDestPaths())

    def test_E_CdslSourcePaths(self):
        for cdsl in repository.getCdsls():
            print "sourcepaths(%s): %s" %(cdsl, cdsl.getSourcePaths())

    def test_F_getChilds(self):
        from comoonics.cdsl.ComCdslRepository import CdslNotFoundException
        try:
            cdsl = repository.getCdsl("hostdependent_dir/shared_dir")
            resultchilds= [ "hostdependent_dir/shared_dir/hostdependent_dir",
                            "hostdependent_dir/shared_dir/hostdependent_file" ]
            for child in cdsl.getChilds():
                self.assertTrue(child.src in resultchilds, "Could not find child cdsl %s for parent cdsl %s." %(cdsl, child))
        except CdslNotFoundException:
            self.assert_("Could not find cdsl under \"hostdependent_dir/shared_dir/hostdependent_dir\".")

    def test_Y_CdslsDeleteNoForce(self):
        import shutil
        from comoonics.cdsl import cmpbysubdirs
        _cdslsrev=repository.getCdsls()
        _cdslsrev.sort(cmpbysubdirs)
        _cdslsrev.reverse()
        for _cdsl in _cdslsrev:
            print "- %s\n" %_cdsl.src
            _cdsl.delete(True, False)
            _files2remove=list()
            if _cdsl.isHostdependent():
                for nodeid in setupCluster.clusterinfo.getNodeIdentifiers('id'):
                    _file="%s.%s" %(_cdsl.src, nodeid)
                    _files2remove.append(_file)
            setupCdsls.repository.workingdir.pushd()
            for _file in _files2remove:
                print "- %s" %_file
                if os.path.isdir(_file):
                    shutil.rmtree(_file)
#                    os.removedirs(_file)
                else:
                    os.remove(_file)
            if _cdsl.isHostdependent():
                shutil.move("%s.%s" %(_cdsl.src, "default"), _cdsl.src)
            setupCdsls.repository.workingdir.popd()
            _cdsl.commit()
            self.assertTrue(_cdsl.exists(), "%s CDSL %s does not exist although it was created before." %(_cdsl.type, _cdsl))
            for __cdsl in setupCdsls.repository.getCdsls():
                self.assertTrue(__cdsl.exists(), "The still existant %s cdsl %s does not exist any more." %(__cdsl.type, __cdsl))

#    def test_Z_CdslsDelete(self):
#        from comoonics.cdsl import cmpbysubdirs
#        _cdslsrev=repository.getCdsls()
#        _cdslsrev.sort(cmpbysubdirs)
#        _cdslsrev.reverse()
#        for _cdsl in _cdslsrev:
#            print "- %s\n" %_cdsl.src
#            setupCdsls.repository.workingdir.pushd()
#            _cdsl.delete(True, True)
#            self.assertFalse(_cdsl.exists(), "%s CDSL %s exists although it was removed before." %(_cdsl.type, _cdsl))
#            for __cdsl in  repository.getCdsls():
#                self.assertTrue(__cdsl.exists(), "The still existant %s cdsl %s does not exist any more." %(__cdsl.type, __cdsl))
#            setupCdsls.repository.workingdir.popd()

if __name__ == "__main__":
    from comoonics.cdsl.ComCdslRepository import ComoonicsCdslRepository
    import os
    #import sys;sys.argv = ['', 'Test.testName']
    setupCluster=setup.SetupCluster()        
    repository=ComoonicsCdslRepository(clusterinfo=setupCluster.clusterinfo, root=setup.tmppath, usenodeids="True")  
    setupCdsls=setup.SetupCDSLs(repository)
    repository.buildInfrastructure(setupCluster.clusterinfo)
    setupCdsls.setupCDSLInfrastructure(setup.tmppath, repository, setupCluster.clusterinfo)
    module=setup.MyTestProgram(module=test_Cdsl(methodName='run'))
    if module.result.wasSuccessful():
        setupCdsls.cleanUpInfrastructure(setup.tmppath, repository, setupCluster.clusterinfo)
        setup.cleanup()
    sys.exit(not module.result.wasSuccessful())    
