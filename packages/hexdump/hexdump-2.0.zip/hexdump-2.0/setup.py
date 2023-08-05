from distutils.core import setup

from os.path import dirname, join

ROOT = dirname(__file__)

def get_version(relpath):
    """read version info from file without importing it"""
    from os.path import dirname, join
    # Below is a hack to read text file with cp1252 characters
    # in Python2/3 compatible way. Reading this text file
    # without specifying encoding will fail in Python 3 on some
    # systems (see http://goo.gl/5XmOH). Specifying encoding as
    # as open() parameter is incompatible with Python 2
    for line in open(join(dirname(__file__), relpath), 'rb'):
        line = line.decode('cp1252')
        if '__version__' in line:
            if '"' in line:
                # __version__ = "0.9"
                return line.split('"')[1]
            elif "'" in line:
                return line.split("'")[1]

# Distutils 'API' to ship test data along with hexdump.py
# http://stackoverflow.com/questions/1612733/including-non-python-files-with-setup-py
from distutils.command.install import INSTALL_SCHEMES
for scheme in INSTALL_SCHEMES.values():
  scheme['data'] = scheme['purelib']


setup(
    name='hexdump',
    version=get_version('hexdump.py'),
    author='anatoly techtonik <techtonik@gmail.com>',
    url='http://bitbucket.org/techtonik/hexdump/',

    description="dump and restore binary data in hex form",
    license="Public Domain",
    classifiers=[
        #'Environment :: Console',
        'License :: Public Domain',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules',
        #'Topic :: Utilities',
    ],

    py_modules=['hexdump'],
    data_files=[('', ['hexfile.bin'])],

    long_description=open(join(ROOT, 'README.txt')).read(),
)
