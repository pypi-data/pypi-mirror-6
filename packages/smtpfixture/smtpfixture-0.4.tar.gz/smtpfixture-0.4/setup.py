#-*- coding: utf-8 -*-

import re
import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
name = 'smtpfixture'

with open(os.path.join(here, 'README.rst')) as file_:
    README = file_.read()
with open(os.path.join(here, 'CHANGES.rst')) as file_:
    CHANGES = file_.read()
with open(os.path.join(here, *(name.split('.') + ['__init__.py']))) as file_:
    version = re.compile(r".*__version__ = '(.*?)'",
                         re.S).match(file_.read()).group(1)


setup(name=name,
      version=version,
      description='SMTP Server that keep all email',
      long_description=README + '\n\n' + CHANGES,
      classifiers=['Programming Language :: Python',
                   'Programming Language :: Python :: 2.7',
                   'License :: OSI Approved :: BSD License',
                   ],
      author='Guillaume Gauvrit',
      author_email='guillaume@gauvr.it',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=['Twisted'],
      entry_points="""\
[console_scripts]
smtpfixture-installdir = smtpfixture:installdir
""",
      )
