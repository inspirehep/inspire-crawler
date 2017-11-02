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
from scrapyd_api.exceptions import ScrapydResponseError

from . import models
from .tasks import schedule_crawl
from .utils import list_spiders


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
@click.option('--tail', default=50, help='Number of entries to show.')
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
    crawler_job = models.CrawlerJob.query.filter_by(id=id).one_or_none()
    if crawler_job is None:
        click.secho(
            (
                "CrawlJob %s was not found, maybe it's not a crawl job?" %
                id
            ),
            fg='yellow',
        )
        sys.exit(1)

    if crawler_job.logs is None:
        click.secho(
            (
                "CrawlJob %s has no log, it might be that it has not run "
                "yet, you can try again later." %
                id
            ),
            fg='yellow',
        )
        sys.exit(1)

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
@click.option('--tail', default=50, help='Number of entries to show.')
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


@crawler.command('schedule')
@click.argument('spider_name')
@click.argument('workflow_name')
@click.option(
    '--dont-force-crawl',
    is_flag=True,
    help=(
        'If it should use the crawl-once mechanisms and crawl the item only '
        'when it was not crawled before.'
    ),
)
@click.option('--kwarg', multiple=True)
@with_appcontext
def schedule_crawl_cli(spider_name, workflow_name, dont_force_crawl, kwarg):
    """Schedule a new crawl.

    Note:
        Currently the oaiharvesting is done on inspire side, before this, so
        it's not supported here yet.
    """
    extra_kwargs = {}
    for extra_kwarg in kwarg:
        if '=' not in extra_kwarg:
            raise TypeError(
                'Bad formatted kwarg (%s), it should be in the form:\n'
                '    --kwarg key=value' % extra_kwarg
            )
        key, value = extra_kwarg.split('=', 1)

        extra_kwargs[key] = value

    settings = {'CRAWL_ONCE_ENABLED': False}
    if dont_force_crawl:
        settings = {}

    try:
        crawler_job = schedule_crawl(
            spider=spider_name,
            workflow=workflow_name,
            crawler_settings=settings,
            **extra_kwargs
        )
    except ScrapydResponseError as error:
        message = str(error)
        if 'spider' in message and 'not found' in message:
            click.echo('%s' % error)
            click.echo('\n Available spiders:')
            spiders = list_spiders()
            click.echo('\n'.join(spiders))
            raise click.Abort()
        else:
            raise

    click.echo(
        'Once the job is started, you can see the logs of the job with the '
        'command:\n'
        '    inspirehep crawler job list\n'
        '    inspirehep crawler job logs %s\n'
        '\n'
        'and for the associated workflow (it\'s job_id should be %s):\n'
        '    inspirehep crawler workflow list\n'
        % (crawler_job.id, crawler_job.id)
    )


@crawler.command('list-spiders')
@with_appcontext
def list_spiders_cli():
    """Show the list of currently available spiders in the scrapyd server.
    """
    spiders = list_spiders
    click.echo('\n'.join(spiders))
