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

import os
import pkg_resources
import pytest
import responses
import json
import uuid

from mock import MagicMock, PropertyMock

from six.moves.urllib.parse import urlparse

from invenio_workflows.models import WorkflowObject
from inspire_crawler.models import JobStatus, CrawlerJob
from inspire_crawler.tasks import submit_results
from inspire_crawler.errors import (
    CrawlerInvalidResultsPath,
    CrawlerJobNotExistError,
    CrawlerScheduleError,
)
from inspire_crawler.receivers import receive_oaiharvest_job


@pytest.fixture()
def sample_record():
    """Provide file fixture."""
    return pkg_resources.resource_string(
        __name__,
        os.path.join(
            'fixtures',
            'records.jl'
        )
    )


@pytest.fixture()
def sample_record_filename():
    """Provide file fixture."""
    return "file://" + pkg_resources.resource_filename(
        __name__,
        os.path.join(
            'fixtures',
            'records.jl'
        )
    )


def test_tasks(app, db, halt_workflow, sample_record_filename):
    """Test tasks."""
    job_id = uuid.uuid4().hex  # init random value
    with app.app_context():
        with pytest.raises(CrawlerInvalidResultsPath):
            submit_results(job_id, "")
        with pytest.raises(CrawlerJobNotExistError):
            submit_results(job_id, sample_record_filename)

        CrawlerJob.create(
            job_id=job_id,
            spider="Test",
            workflow=halt_workflow.__name__,
        )
        db.session.commit()

    with app.app_context():
        job = CrawlerJob.get_by_job(job_id)

        assert job
        assert str(job.status)
        assert job.status == JobStatus.PENDING

        submit_results(job_id, sample_record_filename)

        workflow = WorkflowObject.query.get(1)
        assert workflow
        assert workflow.extra_data['crawler_job_id'] == job_id
        crawler_results_path = workflow.extra_data['crawler_results_path']
        assert crawler_results_path == urlparse(sample_record_filename).path


@responses.activate
def test_receivers(app, db, sample_record):
    """Test receivers."""
    job_id = uuid.uuid4().hex
    responses.add(
        responses.POST, "http://localhost:6800/schedule.json",
        body=json.dumps({"jobid": job_id, "status": "ok"}),
        status=200
    )

    mock_record = MagicMock()
    prop_mock = PropertyMock(return_value=sample_record)
    type(mock_record).raw = prop_mock
    with app.app_context():
        assert receive_oaiharvest_job(
            request=None, records=[mock_record], name=""
        ) is None

        receive_oaiharvest_job(
            request=None,
            records=[mock_record],
            name="",
            spider="Test",
            workflow="test"
        )
        job = CrawlerJob.get_by_job(job_id)

        assert job


@responses.activate
def test_receivers_exception(app, db, sample_record):
    """Test receivers."""
    responses.add(
        responses.POST, "http://localhost:6800/schedule.json",
        body=json.dumps({"jobid": None, "status": "ok"}),
        status=200
    )

    mock_record = MagicMock()
    prop_mock = PropertyMock(return_value=sample_record)
    type(mock_record).raw = prop_mock

    with app.app_context():
        with pytest.raises(CrawlerScheduleError):
            receive_oaiharvest_job(
                request=None,
                records=[mock_record],
                name="",
                spider="Test",
                workflow="test"
            )
