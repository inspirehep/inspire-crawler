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

import json
import os

from six.moves.urllib.parse import urlparse

from celery import shared_task

from flask import current_app

from invenio_db import db

from invenio_workflows.proxies import workflow_object_class

from .errors import (
    CrawlerInvalidResultsPath,
    CrawlerJobError,
    CrawlerScheduleError,
)
from .models import CrawlerJob, JobStatus, CrawlerWorkflowObject


@shared_task(ignore_results=True)
def submit_results(job_id, results_uri, errors, log_file):
    """Check results for current job."""
    results_path = urlparse(results_uri).path
    if not os.path.exists(results_path):
        raise CrawlerInvalidResultsPath(
            "Path specified in result does not exist: {0}".format(results_path)
        )
    job = CrawlerJob.get_by_job(job_id)
    job.logs = log_file
    job.results = results_uri

    if errors:
        job.status = JobStatus.ERROR
        job.save()
        db.session.commit()
        raise CrawlerJobError(str(errors))

    with open(results_path) as records:
        for line in records.readlines():
            record = json.loads(line)
            obj = workflow_object_class.create(data=record)
            obj.extra_data['crawler_job_id'] = job_id
            obj.extra_data['crawler_results_path'] = results_path
            obj.extra_data['record_extra'] = record.pop('extra_data', {})
            obj.data_type = current_app.config['CRAWLER_DATA_TYPE']
            obj.save()
            db.session.commit()

            crawler_object = CrawlerWorkflowObject(
                job_id=job_id, object_id=obj.id
            )
            db.session.add(crawler_object)
            obj.start_workflow(job.workflow, delayed=True)

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
        CrawlerJob.create(
            job_id=job_id,
            spider=spider,
            workflow=workflow,
        )
        db.session.commit()
        current_app.logger.info("Scheduled job {0}".format(job_id))
    else:
        raise CrawlerScheduleError(
            "Could not schedule '{0}' spider for project '{1}'".format(
                spider, current_app.config.get('CRAWLER_PROJECT')
            )
        )
