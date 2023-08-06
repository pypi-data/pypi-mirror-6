from distutils.core import setup

setup(
      name = 'PyAwk'
    , py_modules = ['pyawk']
    , scripts = ['pyawk.py']
    , version = '0.1.0'
    , license = 'LGPL'
    , platforms = ['MacOS', 'POSIX']
    , description = 'You can use python as if it is awk with PyAwk.'
    , author = 'hideshi'
    , author_email = 'hideshi.ogoshi@gmail.com'
    , url = 'https://github.com/hideshi/PyAwk'
    , keywords = ['Awk', 'Console']
    , classifiers = [
          'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)'
        , 'Operating System :: MacOS :: MacOS X'
        , 'Operating System :: POSIX :: Linux'
        , 'Programming Language :: Python'
        , 'Development Status :: 4 - Beta'
        , 'Environment :: Console'
        , 'Intended Audience :: Developers'
        , 'Intended Audience :: System Administrators'
        , 'Topic :: Software Development :: Libraries :: Application Frameworks'
        ]
    , long_description = '''\
You can use python as if it is awk with PyAwk.

Requirements
------------
* Python 3.3 or later

Features
--------
* nothing

Setup
-----
::

   $ pip install PyAwk

   History
   -------
   0.1.0 (2014-02-21)
   ~~~~~~~~~~~~~~~~~~
   * first release
'''
)
