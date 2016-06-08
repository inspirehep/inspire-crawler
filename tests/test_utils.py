# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
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

"""Module tests."""

from __future__ import absolute_import, print_function

from mock import MagicMock, PropertyMock

from inspire_crawler.utils import get_crawler_instance, write_to_dir


def test_utils(app):
    """Test tasks."""
    with app.app_context():
        assert get_crawler_instance()


def test_write_to_dir(app, tmpdir):
    """Test dir creation."""
    mock_record = MagicMock()
    prop_mock = PropertyMock(return_value="foo")
    type(mock_record).raw = prop_mock

    mock_record_2 = MagicMock()
    prop_mock = PropertyMock(return_value="bar")
    type(mock_record_2).raw = prop_mock
    with app.app_context():
        files, total = write_to_dir([mock_record], tmpdir.dirname)
        assert len(files) == 1
        assert total == 1

        files, total = write_to_dir(
            [mock_record, mock_record_2], tmpdir.dirname, max_records=1
        )
        assert len(files) == 2
        assert total == 2

        files, total = write_to_dir([], tmpdir.dirname, max_records=1)
        assert len(files) == 0
        assert total == 0
