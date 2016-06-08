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

"""Utility functions for interfacing with the crawler."""

from __future__ import absolute_import, print_function

import codecs

from flask import current_app

from scrapyd_api import ScrapydAPI

from invenio_oaiharvester.utils import check_or_create_dir, create_file_name


def get_crawler_instance(*args, **kwargs):
    """Return current search client."""
    return ScrapydAPI(
        current_app.config.get('CRAWLER_HOST_URL'),
        *args,
        **kwargs
    )


def write_to_dir(records, output_dir, max_records=1000, encoding='utf-8'):
    """Check if the output directory exists, and creates it if it does not.

    :param records: harvested records.
    :param output_dir: directory where the output should be sent.
    :param max_records: max number of records to be written in a single file.

    :return: paths to files created, total number of records
    """
    if not records:
        return [], 0

    output_path = check_or_create_dir(output_dir)

    files_created = [create_file_name(output_path)]
    total = 0  # total number of records processed
    f = codecs.open(files_created[0], 'w+', encoding=encoding)
    f.write('<ListRecords>')
    for record in records:
        total += 1
        if total > 1 and total % max_records == 0:
            # we need a new file to write to
            f.close()
            files_created.append(create_file_name(output_path))
            f = codecs.open(files_created[-1], 'w+', encoding=encoding)
        f.write(record.raw)
    f.write('</ListRecords>')
    f.close()
    return files_created, total
