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

"""Celery tasks for dealing with crawler."""

from __future__ import absolute_import, print_function

import copy
import json
import os

from six.moves.urllib.parse import urlparse

from celery import shared_task

from flask import current_app

from invenio_db import db

from invenio_workflows import ObjectStatus
from invenio_workflows.proxies import workflow_object_class
from invenio_workflows.tasks import start

from .errors import (
    CrawlerInvalidResultsPath,
    CrawlerJobError,
    CrawlerScheduleError,
)
from .models import CrawlerJob, JobStatus, CrawlerWorkflowObject


@shared_task(ignore_results=True)
def submit_results(job_id, errors, log_file, results_uri, results_data=None):
    """Receive the submission of the results of a crawl job.

    Then it spawns the appropiate workflow according to whichever workflow
    the crawl job specifies.

    :param job_id: Id of the crawler job.
    :param errors: Errors that happened, if any (seems ambiguous)
    :param log_file: Path to the log file of the crawler job.
    :param results_uri: URI to the file containing the results of the crawl
       job, namely the records extracted.
    :param results_data: Optional data payload with the results list, to skip
        retrieving them from the `results_uri`, useful for slow or unreliable
        storages.
    """
    def _extract_results_data(results_path):
        if not os.path.exists(results_path):
            raise CrawlerInvalidResultsPath(
                "Path specified in result does not exist: {0}".format(
                    results_path
                )
            )

        current_app.logger.info(
            'Parsing records from {}'.format(results_path)
        )
        results_data = []
        with open(results_path) as records:
            lines = (
                line.strip() for line in records if line.strip()
            )

            for line in lines:
                current_app.logger.debug(
                    'Reading record line: {}'.format(line)
                )
                record = json.loads(line)
                results_data.append(record)

        current_app.logger.debug(
            'Read {} records from {}'.format(len(results_data), results_path)
        )
        return results_data

    results_path = urlparse(results_uri).path
    job = CrawlerJob.get_by_job(job_id)
    job.logs = log_file
    job.results = results_uri

    if errors:
        job.status = JobStatus.ERROR
        job.save()
        db.session.commit()
        raise CrawlerJobError(str(errors))

    if results_data is None:
        results_data = _extract_results_data(results_path)

    for record in results_data:
        current_app.logger.debug(
            'Parsing record: {}'.format(record)
        )
        record_error = record.get('error')
        if record_error is not None:
            obj = workflow_object_class.create(data=record['xml_record'])
            obj.status = ObjectStatus.ERROR
            obj.extra_data['_error_msg'] = record_error
            obj.extra_data['callback_result'] = record['traceback']
        else:
            obj = workflow_object_class.create(data=record)
            extra_data = {
                'crawler_job_id': job_id,
                'crawler_results_path': results_path,
            }
            record_extra = record.pop('extra_data', {})
            if record_extra:
                extra_data['record_extra'] = record_extra

            obj.extra_data['source_data'] = {
                'data': copy.deepcopy(record),
                'extra_data': copy.deepcopy(extra_data),
            }
            obj.extra_data.update(extra_data)

        obj.data_type = current_app.config['CRAWLER_DATA_TYPE']
        obj.save()
        db.session.commit()

        crawler_object = CrawlerWorkflowObject(
            job_id=job_id, object_id=obj.id
        )
        db.session.add(crawler_object)
        queue = current_app.config['CRAWLER_CELERY_QUEUE']

        if record_error is None:
            start.apply_async(
                kwargs={
                    'workflow_name': job.workflow,
                    'object_id': obj.id,
                },
                queue=queue,
            )

    current_app.logger.info('Parsed {} records.'.format(len(results_data)))

    job.status = JobStatus.FINISHED
    job.save()
    db.session.commit()


@shared_task(ignore_results=True)
def schedule_crawl(spider, workflow, **kwargs):
    """Schedule a crawl using configuration from the workflow objects."""
    from inspire_crawler.utils import get_crawler_instance

    crawler = get_crawler_instance()
    crawler_settings = current_app.config.get('CRAWLER_SETTINGS')
    crawler_settings.update(kwargs.get("crawler_settings", {}))

    crawler_arguments = kwargs
    crawler_arguments.update(
        current_app.config.get('CRAWLER_SPIDER_ARGUMENTS', {}).get(spider, {})
    )
    job_id = crawler.schedule(
        project=current_app.config.get('CRAWLER_PROJECT'),
        spider=spider,
        settings=crawler_settings,
        **crawler_arguments
    )
    if job_id:
        crawler_job = CrawlerJob.create(
            job_id=job_id,
            spider=spider,
            workflow=workflow,
        )
        db.session.commit()
        current_app.logger.info(
            "Scheduled scrapyd job with id: {0}".format(job_id)
        )
        current_app.logger.info(
            "Created crawler job with id:{0}".format(crawler_job.id)
        )
    else:
        raise CrawlerScheduleError(
            "Could not schedule '{0}' spider for project '{1}'".format(
                spider, current_app.config.get('CRAWLER_PROJECT')
            )
        )

    return str(crawler_job.job_id)
