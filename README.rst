..
    This file is part of Invenio.
    Copyright (C) 2016 CERN.

    Invenio is free software; you can redistribute it
    and/or modify it under the terms of the GNU General Public License as
    published by the Free Software Foundation; either version 2 of the
    License, or (at your option) any later version.

    Invenio is distributed in the hope that it will be
    useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Invenio; if not, write to the
    Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
    MA 02111-1307, USA.

    In applying this license, CERN does not
    waive the privileges and immunities granted to it by virtue of its status
    as an Intergovernmental Organization or submit itself to any jurisdiction.

=================
 inspire-crawler
=================

.. image:: https://img.shields.io/travis/inspirehep/inspire-crawler.svg
        :target: https://travis-ci.org/inspirehep/inspire-crawler

.. image:: https://img.shields.io/coveralls/inspirehep/inspire-crawler.svg
        :target: https://coveralls.io/r/inspirehep/inspire-crawler

.. image:: https://img.shields.io/github/tag/inspirehep/inspire-crawler.svg
        :target: https://github.com/inspirehep/inspire-crawler/releases

.. image:: https://img.shields.io/pypi/dm/inspire-crawler.svg
        :target: https://pypi.python.org/pypi/inspire-crawler

.. image:: https://img.shields.io/github/license/inspirehep/inspire-crawler.svg
        :target: https://github.com/inspirehep/inspire-crawler/blob/master/LICENSE


Crawler integration with INSPIRE-HEP using scrapy project `HEPCrawl`_.

This module allows scheduling of crawler jobs to a `Scrapyd`_ instance serving
a `Scrapy`_ project. E.g. in this case the default scrapy project is `HEPCrawl`_.

It integrates directly with `invenio-workflows`_ module to create workflows for every
record harvested by the crawler.

This module is meant to use only with `INSPIRE-HEP`_ overlay. **Use at own risk.**

Full documentation is hosted here: http://pythonhosted.org/inspire-crawler/

See also documentation of HEPCrawl: http://pythonhosted.org/hepcrawl/

.. _HEPCrawl: http://pythonhosted.org/hepcrawl/
.. _Scrapyd: http://scrapyd.readthedocs.io/
.. _Scrapy: http://doc.scrapy.org/
.. _invenio-workflows: http://pythonhosted.org/invenio-workflows/
.. _INSPIRE-HEP: http://inspirehep.readthedocs.io
