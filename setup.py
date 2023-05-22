# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016, 2017 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Crawler integration with INSPIRE-HEP."""

from __future__ import absolute_import, print_function

from setuptools import find_packages, setup

readme = open('README.rst').read()

tests_require = [
    'check-manifest>=0.25',
    'coverage>=4.0',
    'mock~=2.0,>=2.0.0',
    'pydocstyle>=1.0.0',
    'pytest-cache>=1.0',
    'pytest-cov>=1.8.0',
    'pytest-pep8>=1.0.6',
    'pytest>=2.8.0',
    'requests_mock~=1.0,>=1.4.0',
]

extras_require = {
    'docs': [
        'Sphinx>=1.5,<1.6',
    ],
    'postgresql': [
        'invenio-db[postgresql,versioning]==1.0.4',
        'psycopg2-binary==2.8.4'
    ],
    'mysql': [
        'invenio-db[mysql,versioning]==1.0.4',
    ],
    'sqlite': [
        'invenio-db[versioning]==1.0.4',
    ],
    'tests': tests_require,
}

extras_require['all'] = []
for name, reqs in extras_require.items():
    if name in ('mysql', 'postgresql', 'sqlite'):
        continue
    extras_require['all'].extend(reqs)

setup_requires = [
    'autosemver~=0.2,>=0.2',
    'Babel==2.8.0',
    'pytest-runner==5.2',
]

install_requires = [
    'autosemver~=0.2,>=0.2',
    'six==1.14.0',
    'Flask==0.12.5',
    'python-scrapyd-api==2.1.2',
    'pathlib2==2.3.5',
    'invenio-celery==1.1.0',
    'celery~=4.0,>=4.1.0',
    'invenio_workflows==7.0.6',
    'invenio_workflows_ui==2.0.19',
    'invenio_oaiharvester==1.0.0a4',
    'invenio-files-rest==1.0.5',
    'invenio-access==1.3.0',
    'invenio-accounts==1.1.1',
    'ftfy==4.4.3',
    "invenio-records==1.1.1",
    "invenio-pidstore==1.1.0",
    "SQLAlchemy==1.3.1",
    "Werkzeug==0.16.1",
    "invenio_rest==1.1.3",
    "Flask_Security==3.0.0",
    "Flask-SQLAlchemy @ git+https://github.com/inspirehep/flask-sqlalchemy.git@71abd94a1e2317a1365a25a31e719dbd9aafceea",
    "WTForms==2.2.1",
    "invenio-indexer==1.1.1",
    "SQLAlchemy-Continuum==1.3.9",
    "invenio_db==1.0.4",
    "invenio-records-rest==1.6.4",
    "jsonresolver==0.2.1",
    "Flask-Breadcrumbs==0.4.0",
    "invenio-base==1.2.0",
    "invenio-i18n==1.1.1",
    "invenio-search==1.2.3"
]

packages = find_packages()
URL = 'https://github.com/inspirehep/inspire-crawler'


setup(
    name='inspire-crawler',
    autosemver={
        'bugtracker_url': URL + '/issues/'
    },
    description=__doc__,
    long_description=readme,
    keywords='invenio inspire scrapy crawler',
    license='GPLv2',
    author='CERN',
    author_email='feedback@inspirehep.net',
    url=URL,
    version="3.0.6",
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'invenio_base.api_apps': [
            'inspire_crawler = inspire_crawler:INSPIRECrawler',
        ],
        'invenio_base.apps': [
            'inspire_crawler = inspire_crawler:INSPIRECrawler',
        ],
        'invenio_db.alembic': [
            'inspire_crawler = inspire_crawler:alembic',
        ],
        'invenio_db.models': [
            'inspire_crawler = inspire_crawler.models',
        ],
        'invenio_celery.tasks': [
            'inspire_crawler = inspire_crawler.tasks',
        ],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Development Status :: 1 - Planning',
    ],
)
