import os
import zipfile
import struct

from cStringIO import StringIO

import pytest

from crx.writer import zipdir, sign

here = os.path.abspath(os.path.dirname(__file__))

def test_zipdir():
    data = zipdir(os.path.join(here, 'dirfix'))
    with open('zipout.zip', 'w') as fp:
        fp.write(data)

    zipfile.ZipFile('zipout.zip', 'r') # just don't raise

# This is a dummy private key. It doesn't go anywhere. (..and, should
# be obvious but, for your own sake DO NOT USE IT FOR ANYTHING!!).
goes_nowhere_pem = open('test/goes_nowhere.pkey').read()

def test_sign():
    sign('some data', goes_nowhere_pem) # also, don't raise

@pytest.fixture
def clear_crx():
    if os.path.exists('test-ext.crx'):
        os.unlink('test-ext.crx')

def checkcrx():
    __tracebackhide__ = True
    with open('test-ext.crx', 'rb') as archive:
        assert archive.read(len('Cr24')) == 'Cr24'
        version, keylen, siglen = (
            struct.unpack('<III', archive.read(struct.calcsize('<III'))) )
        assert version == 2
        archive.read(keylen)
        archive.read(siglen)
        assert len(zipfile.ZipFile(StringIO(archive.read())).filelist) == 2

def test_roundtrip_inline_pem(clear_crx):
    import crx
    crx.write('test/dirfix', 'test-ext.crx', pem=goes_nowhere_pem)
    checkcrx()

def test_rountrip_file_pem(clear_crx):
    import crx
    crx.write('test/dirfix', 'test-ext.crx', pemfile='test/goes_nowhere.pkey')
    checkcrx()
