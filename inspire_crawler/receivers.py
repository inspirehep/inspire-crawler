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

import pathlib2

from flask import current_app

from invenio_oaiharvester.signals import oaiharvest_finished

from .tasks import schedule_crawl
from .utils import write_to_dir


@oaiharvest_finished.connect
def receive_oaiharvest_job(request, records, name, **kwargs):
    """Receive a list of harvested OAI-PMH records and schedule crawls."""
    spider = kwargs.get('spider')
    workflow = kwargs.get('workflow')
    if not spider or not workflow:
        return

    files_created, _ = write_to_dir(
        records,
        output_dir=current_app.config['CRAWLER_OAIHARVEST_OUTPUT_DIRECTORY']
    )

    for source_file in files_created:
        # URI is required by scrapy.
        file_uri = pathlib2.Path(source_file).as_uri()
        schedule_crawl(spider, workflow, source_file=file_uri)


__all__ = (
    'receive_oaiharvest_job',
)
