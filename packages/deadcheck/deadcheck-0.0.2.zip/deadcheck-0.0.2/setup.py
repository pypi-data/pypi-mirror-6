'''
Created on Dec 3, 2013

@author: harsnara

@change:     2013-12-03    :    Initial Draft
             2013-12-09    :    Changes Made for release 0.0.2
'''

__version__ = "0.0.2"
__author__ ="Harsha Narayana"
__date__ = "03 Dec 2013"


from distutils.core import setup

setup(name = 'deadcheck',
      version = '0.0.2',
      description = 'Deadlink Check utility using Python.',
      author = 'Harsha Narayana',
      author_email = 'harsha2k4@gmail.com',
      url = 'https://github.com/harshanarayana/deadcheck',
      download_url = 'https://github.com/harshanarayana/deadcheck',
      packages = ['deadcheck'],
      license = 'MIT',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Environment :: Web Environment',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: Python Software Foundation License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Communications :: Email',
          'Topic :: Office/Business',
          'Topic :: Software Development :: Bug Tracking',
          ],
      scripts=['run.py']
      )