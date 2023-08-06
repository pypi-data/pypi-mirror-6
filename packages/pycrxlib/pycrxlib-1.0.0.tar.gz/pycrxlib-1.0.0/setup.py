import subprocess

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

try:
    subprocess.call(['swig', '-version'])
except OSError:
    print("""

***** WARNING: Can't seem to find swig (http://www.swig.org/) on your system.

If the installation fails, try installing it using your system's package
manager (apt-get/brew/rpm etc).

""")

setup(
    name='pycrxlib',
    version='1.0.0',
    description='Integrates generation of .crx files with build systems',
    long_description='\n'.join((
        "Routines for programatically generating Google Chrome .crx files.",
        "Good for Python-based build tools e.g. Fabric, Ansible, Paver and ",
        "possibly others")),
    packages=('crx',),
    url='https://github.com/JacobOscarson/pycrxlib',
    author='Jacob Oscarson',
    author_email='jacob@plexical.com',
    license='MIT',
    classifiers=(
        'Topic :: Software Development :: Build Tools',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ),
    install_requires=('M2Crypto>=0.20.2',),
)
