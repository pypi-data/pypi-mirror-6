import unittest, os, tempfile, shutil
from zope.testing import doctest

def setUp(test):
    test.globs['temp_dir'] = temp_dir = tempfile.mkdtemp()
    test.globs['data_fs'] = data_fs = os.path.join(
        temp_dir, 'Data.fs')
    
def tearDown(test):
    shutil.rmtree(test.globs['temp_dir'])

def test_suite():
    return doctest.DocFileSuite(
        'README.txt',
        setUp=setUp, tearDown=tearDown,
        optionflags=doctest.REPORT_NDIFF)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
