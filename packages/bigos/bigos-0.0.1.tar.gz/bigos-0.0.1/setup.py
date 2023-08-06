#/bin/env python2
# encoding: utf8

import setuptools
from os.path import join, dirname

setuptools.setup(
    name="bigos",
    version="0.0.1",
    packages=["bigos"],
    author=u"Paweł Stiasny",
    author_email="pawelstiasny@gmail.com",
    url="http://github.com/pstiasny/bigos",
    license="GPL",
    description="Do stuff on file change",
    long_description=open(join(dirname(__file__), "README.rst")).read(),
    keywords=['filesystem', 'event', 'task'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Operating System :: POSIX :: Linux',
        'Topic :: System :: Filesystems',
        'Topic :: Utilities',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
)
