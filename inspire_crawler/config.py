# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Configuration for crawler integration."""

from __future__ import absolute_import, print_function


CRAWLER_HOST_URL = "http://localhost:6800"
"""URL to Scrapyd HTTP server."""

CRAWLER_DATA_TYPE = "hep"
"""WorkflowObject `data_type` to set to all workflow objects."""

CRAWLER_PROJECT = "hepcrawl"
"""Scrapy project name to schedule crawls for."""

CRAWLER_SETTINGS = {
    "API_PIPELINE_URL": "http://localhost:5555/api/task/async-apply",
    "API_PIPELINE_TASK_ENDPOINT_DEFAULT": ("inspire_crawler.tasks"
                                           ".submit_results")
}
"""Dictionary of settings to add to crawlers.

By default set to flower tasks HTTP API and the standard task to be called with
the results of the harvesting.
"""

CRAWLER_SPIDER_ARGUMENTS = {}
"""Add any spider arguments to be passed when scheduling tasks.

For example for spider `myspider`:

.. code-block:: python

    {
        'myspider': {'somearg': 'foo'}
    }

You can also pass arguments directly to the scheduler with kwargs.
"""
