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

"""Perform crawler operations such as querying crawler jobs."""

from __future__ import absolute_import, print_function

import os
import sys

import click
from flask.cli import with_appcontext
from invenio_db import db

from . import models


CRAWLER_JOB_PROPS_TO_IGNORE = [
    'metadata',
    'query',
]


def _show_table(results):
    cols = []
    for result in results:
        if not cols:
            cols = _extract_cols_from_instance(result)
            click.secho('    '.join(cols), fg='blue')

        values = [
            str(getattr(result, col))
            for col in cols
        ]
        click.echo('    '.join(values))


def _show_file(file_path, header_name='Shown'):
    if file_path.startswith('file:/'):
        file_path = file_path[6:]

    click.secho("%s file: %s" % (header_name, file_path), fg='blue')
    if not os.path.exists(file_path):
        click.secho('    The file does not exist', fg='yellow')
    else:
        with open(file_path) as fd:
            click.echo_via_pager(fd.read())


@click.group()
def crawler():
    """Crawler commands."""


def _extract_cols_from_instance(instance):
    cols = [
        prop for prop in dir(instance)
        if not prop.startswith('_') and
        not callable(getattr(instance, prop)) and
        prop not in CRAWLER_JOB_PROPS_TO_IGNORE

    ]
    return cols


@crawler.group()
def job():
    """CrawlerJob commands."""


@job.command('list')
@click.option('--tail', default=0, help='Number of entries to show.')
@with_appcontext
def list_jobs(tail):
    """Show info about the existing crawler jobs."""
    query = (
        db.session.query(models.CrawlerJob)
        .order_by(models.CrawlerJob.id.desc())
    )
    if tail != 0:
        query = query.limit(tail)

    results = query.yield_per(10).all()
    _show_table(results=results)


@job.command('logs')
@click.argument('id')
@with_appcontext
def get_job_logs(id):
    """Get the crawl logs from the job."""
    crawler_job = models.CrawlerJob.query.filter_by(id=id).one()
    _show_file(
        file_path=crawler_job.logs,
        header_name='Log',
    )


@job.command('results')
@click.argument('id')
@with_appcontext
def get_job_results(id):
    """Get the crawl results from the job."""
    crawler_job = models.CrawlerJob.query.filter_by(id=id).one()
    _show_file(
        file_path=crawler_job.results,
        header_name='Results',
    )


@crawler.group()
def workflow():
    """CrawlerWorkflowObject commands."""


@workflow.command('list')
@click.option('--tail', default=0, help='Number of entries to show.')
@with_appcontext
def list_crawler_workflows(tail):
    """Show info about the existing crawler workflows."""
    query = (
        models.CrawlerWorkflowObject.query
        .order_by(models.CrawlerWorkflowObject.object_id.desc())
    )
    if tail != 0:
        query = query.limit(tail)

    workflows = query.yield_per(10).all()
    _show_table(results=workflows)


@workflow.command('get_job_logs')
@click.argument('workflow_id')
@with_appcontext
def get_job_logs_from_workflow(workflow_id):
    """Retrieve the crawl logs from the workflow id."""
    query_result = (
        db.session.query(
            models.CrawlerJob.logs,
        )
        .join(
            models.CrawlerWorkflowObject,
            models.CrawlerJob.job_id == models.CrawlerWorkflowObject.job_id,
        )
        .filter(models.CrawlerWorkflowObject.object_id == workflow_id)
        .one_or_none()
    )

    if query_result is None:
        click.secho(
            (
                "Workflow %s was not found, maybe it's not a crawl workflow?" %
                workflow_id
            ),
            fg='yellow',
        )
        sys.exit(1)

    _show_file(
        file_path=query_result[0],
        header_name='Log',
    )


@workflow.command('get_job_results')
@click.argument('workflow_id')
@with_appcontext
def get_job_results_from_workflow(workflow_id):
    """Retrieve the crawl results from the workflow id."""
    query_result = (
        db.session.query(
            models.CrawlerJob.results,
        )
        .join(
            models.CrawlerWorkflowObject,
            models.CrawlerJob.job_id == models.CrawlerWorkflowObject.job_id,
        )
        .filter(models.CrawlerWorkflowObject.object_id == workflow_id)
        .one_or_none()
    )

    if query_result is None:
        click.secho(
            (
                "Workflow %s was not found, maybe it's not a crawl workflow?" %
                workflow_id
            ),
            fg='yellow',
        )
        sys.exit(1)

    _show_file(
        file_path=query_result[0],
        header_name='Results',
    )
