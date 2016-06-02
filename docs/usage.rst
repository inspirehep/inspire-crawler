..
    This file is part of Invenio.
    Copyright (C) 2016 CERN.

    Invenio is free software; you can redistribute it
    and/or modify it under the terms of the GNU General Public License as
    published by the Free Software Foundation; either version 2 of the
    License, or (at your option) any later version.

    Invenio is distributed in the hope that it will be
    useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Invenio; if not, write to the
    Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
    MA 02111-1307, USA.

    In applying this license, CERN does not
    waive the privileges and immunities granted to it by virtue of its status
    as an Intergovernmental Organization or submit itself to any jurisdiction.


Usage
=====

After installing `inspire-crawler`, there is already a signal receiver attached
to the `invenio-oaiharvester`_ module `oaiharvest_finished` signal.

This will execute the function :py:meth:`inspire_crawler.receivers.receive_oaiharvest_job` which will check
for certain arguments (spider name and workflow name) and schedule a crawl job.

Basically you just need to schedule crawls with :py:meth:`inspire_crawler.tasks.schedule_crawl` and required
arguments:

  * spider:  name of spider to execute
  * workflow: name of workflow to execute when receiving crawled items


If you want to hook in other ways to automatically schedule crawler jobs, you can for example use
`CELERYBEAT_SCHEDULE`_ in your Flask configuration:

.. code-block:: python

    CELERYBEAT_SCHEDULE = {
      # Crawl World Scientific every Sunday at 2 AM
      'world-scientific-sunday': {
        'task': 'inspire_crawler.tasks.schedule_crawl',
        'schedule': crontab(minute=0, hour=2, day_of_week=0),
        'kwargs': {
            "spider": "WSP",
            "workflow": "my_ingestion_workflow",
            "ftp_host": "ftp.example.com",
            "ftp_netrc": "/some/folder/netrc"
        }
      }
    }

.. note::

    You need to provide the arguments ``spider`` and ``workflow`` alongside any other
    spider arguments.




.. _invenio-oaiharvester: http://pythonhosted.org/invenio-oaiharvester/
.. _CELERYBEAT_SCHEDULE: http://docs.celeryproject.org/en/latest/configuration.html#std:setting-CELERYBEAT_SCHEDULE
