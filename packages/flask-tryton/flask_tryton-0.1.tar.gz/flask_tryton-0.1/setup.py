#This file is part of flask_tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='flask_tryton',
    version='0.1',
    author='B2CK',
    author_email='info@b2ck.com',
    url='http://code.google.com/p/flask-tryton/',
    description='Adds Tryton support to Flask application',
    long_description=read('README'),
    py_modules=['flask_tryton'],
    zip_safe=False,
    platforms='any',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Tryton',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
        ],
    license='GPL-3',
    install_requires=[
        'Flask>=0.8',
        'trytond>=3.0',
        ],
    )
