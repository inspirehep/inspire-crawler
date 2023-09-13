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
import json
import uuid

from mock import MagicMock, PropertyMock, patch

import requests_mock
from six.moves.urllib.parse import urlparse

from invenio_workflows import WorkflowObject, ObjectStatus
from inspire_crawler.models import JobStatus, CrawlerJob, CrawlerWorkflowObject
from inspire_crawler.tasks import submit_results
from inspire_crawler.errors import (
    CrawlerInvalidResultsPath,
    CrawlerJobNotExistError,
    CrawlerScheduleError,
    CrawlerJobError,
)
from inspire_crawler.receivers import receive_oaiharvest_job


@pytest.fixture()
def sample_records_filename():
    return pkg_resources.resource_filename(
        __name__,
        os.path.join(
            'fixtures',
            'records.jl'
        )
    )


@pytest.fixture()
def sample_records_uri(sample_records_filename):
    return "file://" + sample_records_filename


@pytest.fixture()
def sample_records(sample_records_filename):
    with open(sample_records_filename) as records_fd:
        records = (
            json.loads(line.strip()) for line in records_fd.readlines()
            if line.strip()
        )

    return list(records)


@pytest.fixture()
def sample_record_string(sample_records_filename):
    with open(sample_records_filename) as records_fd:
        line = records_fd.readline()

    return line


def test_tasks(app, db, halt_workflow, sample_records_uri):
    """Test tasks."""
    job_id = uuid.uuid4().hex  # init random value
    with app.app_context():
        with pytest.raises(CrawlerJobNotExistError):
            submit_results(
                job_id, results_uri=sample_records_uri,
                errors=None, log_file=None, spider_name="test"
            )

        CrawlerJob.create(
            job_id=job_id,
            spider="Test",
            workflow=halt_workflow.__name__,
            logs=None,
            results=None,
        )
        db.session.commit()

        with pytest.raises(CrawlerInvalidResultsPath):
            submit_results(
                job_id,
                results_uri="",
                errors=None,
                log_file=None,
                spider_name='test'
            )

    with app.app_context():
        job = CrawlerJob.get_by_job(job_id)
        assert job
        assert str(job.status)
        assert job.status == JobStatus.PENDING

        submit_results(
            job_id=job_id,
            results_uri=sample_records_uri,
            errors=None,
            log_file="/foo/bar",
            spider_name='Test'
        )

        job = CrawlerJob.get_by_job(job_id)
        assert job.logs == "/foo/bar"
        assert job.results == sample_records_uri

        workflow = WorkflowObject.get(1)
        assert workflow
        extra_data = workflow.extra_data
        assert 'source_data' in extra_data
        assert 'data' in extra_data['source_data']
        assert 'extra_data' in extra_data['source_data']
        expected_extra_data = {
            'crawler_job_id': job_id,
            'crawler_results_path': urlparse(sample_records_uri).path,
            'source_file': 'desy_records.xml'
        }
        assert expected_extra_data == extra_data['source_data']['extra_data']

        with pytest.raises(CrawlerJobError):
            submit_results(
                job_id,
                results_uri=sample_records_uri,
                errors=["Some error"],
                log_file=None,
                spider_name='test'
            )

        job = CrawlerJob.get_by_job(job_id)
        assert job.status == JobStatus.ERROR


def test_submit_results_with_results_data(app, db, halt_workflow,
                                          sample_records_uri, sample_records):
    """Test submit_results passing the data as payload."""
    job_id = uuid.uuid4().hex  # init random value
    with app.app_context():
        CrawlerJob.create(
            job_id=job_id,
            spider="Test",
            workflow=halt_workflow.__name__,
            logs=None,
            results=None,
        )
        db.session.commit()

    with app.app_context():
        job = CrawlerJob.get_by_job(job_id)
        assert job
        assert str(job.status)
        assert job.status == JobStatus.PENDING

        dummy_records_uri = sample_records_uri + 'idontexist'
        submit_results(
            job_id=job_id,
            results_uri=dummy_records_uri,
            results_data=sample_records,
            errors=None,
            log_file="/foo/bar",
            spider_name='Test'
        )

        job = CrawlerJob.get_by_job(job_id)
        assert job.logs == "/foo/bar"
        assert job.results == dummy_records_uri

        workflow = WorkflowObject.get(1)
        assert workflow
        assert workflow.extra_data['crawler_job_id'] == job_id
        crawler_results_path = workflow.extra_data['crawler_results_path']
        assert crawler_results_path == urlparse(dummy_records_uri).path

        with pytest.raises(CrawlerJobError):
            submit_results(
                job_id,
                results_uri=dummy_records_uri,
                results_data=sample_records,
                errors=["Some error"],
                log_file=None,
                spider_name='Test'
            )

        job = CrawlerJob.get_by_job(job_id)
        assert job.status == JobStatus.ERROR


def test_receivers(app, db, sample_record_string):
    with requests_mock.Mocker() as requests_mocker:
        job_id = uuid.uuid4().hex

        requests_mocker.register_uri(
            'POST', 'http://localhost:6800/schedule.json',
            json={'jobid': job_id, 'status': 'ok'})

        mock_record = MagicMock()
        prop_mock = PropertyMock(return_value=sample_record_string)
        type(mock_record).raw = prop_mock

        with app.app_context():
            assert receive_oaiharvest_job(
                request=None, records=[mock_record], name=""
            ) is None

            receive_oaiharvest_job(
                request=None,
                records=[mock_record],
                name='',
                spider='Test',
                workflow='test'
            )
            job = CrawlerJob.get_by_job(job_id)

            assert job


def test_receivers_exception(app, db, sample_record_string):
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri(
            'POST', 'http://localhost:6800/schedule.json',
            json={'jobid': None, 'status': 'ok'})

        mock_record = MagicMock()
        prop_mock = PropertyMock(return_value=sample_record_string)
        type(mock_record).raw = prop_mock

        with app.app_context():
            with pytest.raises(CrawlerScheduleError):
                receive_oaiharvest_job(
                    request=None,
                    records=[mock_record],
                    name='',
                    spider='Test',
                    workflow='test'
                )


def test_create_workflow_for_faulty_data(app, db, halt_workflow):
    """Test submit_results passing the data as payload."""
    job_id = uuid.uuid4().hex  # init random value
    with app.app_context():
        CrawlerJob.create(
            job_id=job_id,
            spider="desy",
            workflow=halt_workflow.__name__,
            logs=None,
            results=None,
        )
        db.session.commit()

    with app.app_context():
        job = CrawlerJob.get_by_job(job_id)
        assert job
        assert str(job.status)
        assert job.status == JobStatus.PENDING

        test_data = {
            'errors': [
                {
                    'exception': 'ValueError',
                    'traceback': 'ValueError on the line 23.'
                }
            ],
            'source_data': 'Just an XML string',
            'record': {},
            'file_name': 'broken.xml'
        }
        submit_results(
            job_id=job_id,
            results_uri='idontexist',
            results_data=[test_data],
            errors=None,
            log_file="/foo/bar",
            spider_name='test'
        )
        workflow_id = CrawlerWorkflowObject.query.filter_by(job_id=job_id) \
            .one().object_id
        workflow = WorkflowObject.get(workflow_id)

        expected_crawl_error = {
            'errors': [
                {
                    'exception': 'ValueError',
                    'traceback': 'ValueError on the line 23.'
                }
            ],
            'source_data': 'Just an XML string',
            'file_name': 'broken.xml'
        }

        assert workflow.status == ObjectStatus.ERROR
        assert workflow.data == test_data['record']
        assert workflow.extra_data['crawl_errors'] == expected_crawl_error


def test_create_error_workflow_for_wrong_crawl_result(app, db, halt_workflow):
    job_id = uuid.uuid4().hex  # init random value
    with app.app_context():
        CrawlerJob.create(
            job_id=job_id,
            spider="desy",
            workflow=halt_workflow.__name__,
            logs=None,
            results=None,
        )
        db.session.commit()

    with app.app_context():
        job = CrawlerJob.get_by_job(job_id)
        assert job
        assert str(job.status)
        assert job.status == JobStatus.PENDING

        test_data = {
            'source_data': 'Just an XML string',
            'record': {},
            # missing 'errors' and 'file_name'
        }
        submit_results(
            job_id=job_id,
            results_uri='idontexist',
            results_data=[test_data],
            errors=None,
            log_file="/foo/bar",
            spider_name='desy'
        )
        workflow_id = CrawlerWorkflowObject.query.filter_by(job_id=job_id) \
            .one().object_id
        workflow = WorkflowObject.get(workflow_id)

        expected = {
            'errors': [
                {
                    'exception': 'KeyError',
                    'traceback': 'Wrong crawl result format. '
                                 'Missing the key `errors`'
                }
            ],
            'file_name': None,
            'source_data': {'record': {}, 'source_data': 'Just an XML string'},
        }

        assert workflow.status == ObjectStatus.ERROR
        assert workflow.data == {}
        assert workflow.extra_data['crawl_errors'] == expected


@patch('inspire_crawler.tasks.start.apply_async')
def test_submit_results_put_task_in_corrct_queue(
    mock_submit_results,
    app,
    db,
    halt_workflow,
    sample_records_uri
):
    job_id = uuid.uuid4().hex  # init random value
    with app.app_context():
        CrawlerJob.create(
            job_id=job_id,
            spider="Test",
            workflow=halt_workflow.__name__,
            logs=None,
            results=None,
        )
        db.session.commit()
        job = CrawlerJob.get_by_job(job_id)
        assert job
        assert str(job.status)
        assert job.status == JobStatus.PENDING

        submit_results(
            job_id=job_id,
            results_uri=sample_records_uri,
            errors=None,
            log_file="/foo/bar",
            spider_name='desy'
        )
        assert mock_submit_results.call_args[1]['queue'] == 'desy-harvest'
