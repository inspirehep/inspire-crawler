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
    """Write the given records iterable to the out dir.

    :param records: iterable with the harvested records.
    :param output_dir: directory where the output should be sent.
    :param max_records: max number of records to be written in a single file.

    :return: tuple with paths to files created, total number of records
    processed.
    """
    def _write_batch(records_iterator, ammount, file_name):
        processed_records = 0
        exhausted = False
        with codecs.open(file_name, 'w+', encoding=encoding) as fd:
            fd.write('<ListRecords>')
            for record in records_iterator:
                fd.write(record.raw)
                processed_records += 1
                if processed_records == ammount:
                    break
            else:
                exhausted = True

            fd.write('</ListRecords>')

        return exhausted, processed_records

    output_path = check_or_create_dir(output_dir)
    processed = 0
    iterator_exhausted = False
    files = []
    while not iterator_exhausted:
        file_name = create_file_name(output_path)
        iterator_exhausted, batch_processed = _write_batch(
            records_iterator=records,
            ammount=max_records,
            file_name=file_name,
        )
        files.append(file_name)
        processed += batch_processed

    return files, processed
