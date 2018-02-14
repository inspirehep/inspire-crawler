# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2018 CERN.
#
# INSPIRE is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

from __future__ import absolute_import, print_function

import json

import requests_mock
from click.testing import CliRunner
from mock import patch

from inspire_crawler.cli import crawler


@patch('inspire_crawler.cli.schedule_crawl')
def test_schedule_crawl_cli(mock_schedule_crawl, script_info):
    mock_schedule_crawl.return_value = '1dd85701-787a-433d-b23f-ea4a16c5b1c0'

    runner = CliRunner()

    result = runner.invoke(
        crawler, ['schedule', 'APS', 'article'], obj=script_info)

    assert 0 == result.exit_code
    assert '1dd85701-787a-433d-b23f-ea4a16c5b1c0' in result.output


def test_list_spiders_cli(script_info):
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri(
            'GET', 'http://localhost:6800/listspiders.json?project=hepcrawl',
            json={'spiders': ['APS', 'BASE', 'CDS'], 'status': 'ok'})

        runner = CliRunner()

        result = runner.invoke(crawler, ['list-spiders'], obj=script_info)

        assert result.exit_code == 0
        assert 'APS\nBASE\nCDS\n' == result.output
