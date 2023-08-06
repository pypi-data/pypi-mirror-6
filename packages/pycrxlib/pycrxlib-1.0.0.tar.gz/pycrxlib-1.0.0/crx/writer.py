import os
import base64
import io
import zipfile
import struct

import M2Crypto

def zipdir(path):
    with io.BytesIO() as stream:
        zfp = zipfile.ZipFile(stream, 'w', zipfile.ZIP_DEFLATED)

        cwd = os.getcwd()
        try:
            os.chdir(path)
            for root, dirs, files in os.walk('.'):
                for name in files:
                    zfp.write(os.path.join(root, name))
        finally:
            os.chdir(cwd)

        zfp.close()
        return stream.getvalue()

def sign(data, pem):
    pkey = M2Crypto.EVP.load_key_string(pem)
    pkey.sign_init()
    pkey.sign_update(data)
    rsakey = M2Crypto.RSA.load_key_string(pem)
    buf = M2Crypto.BIO.MemoryBuffer()
    rsakey.save_pub_key_bio(buf)
    # See http://stackoverflow.com/a/21711195/288672
    return (base64.b64decode(''.join(buf.read().split(os.linesep)[1:-2])),
            pkey.sign_final())

def write(out, data, der_key, signed):
    out.write('Cr24') # magic
    out.write(struct.pack('<III', 2, len(der_key), len(signed)))
    out.write(der_key)
    out.write(signed)
    out.write(data)
