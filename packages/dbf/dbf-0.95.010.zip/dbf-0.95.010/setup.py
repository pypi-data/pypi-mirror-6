from distutils.core import setup
from glob import glob
import os
import dbf

html_docs = glob('dbf/html/*')

long_desc="""
Currently supports dBase III, FoxPro, and Visual FoxPro tables. Text is returned as unicode, and codepage settings in tables are honored. Memos and Null fields are supported.  Documentation needs work, but author is very responsive to e-mails.

Not supported: index files (but can create tempory non-file indexes), auto-incrementing fields, and Varchar fields.

Latest release has many backwards incompatibilities, as well as some documentation.  Hopefully the latter will make the former bareable.
"""

setup( name='dbf',
       version= '%d.%02d.%03d' % dbf.version,
       license='BSD License',
       description='Pure python package for reading/writing dBase, FoxPro, and Visual FoxPro .dbf files (including memos)',
       long_description=long_desc,
       url='http://groups.google.com/group/python-dbase',
       py_modules=['dbf', 'dbf_test'],
       provides=['dbf'],
       author='Ethan Furman',
       author_email='ethan@stoneleaf.us',
       classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Programming Language :: Python',
            'Topic :: Database' ],
     )

