import writer

def write(dirpath, crxpath, pemfile=None, pem=None):
    if pem is None:
        with open(pemfile) as fp:
            pem = fp.read()

    data = writer.zipdir(dirpath)
    der_key, signed = writer.sign(data, pem)

    with open(crxpath, 'w') as out:
        writer.write(out, data, der_key, signed)
