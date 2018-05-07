..
    This file is part of INSPIRE.
    Copyright (C) 2014-2018 CERN.

    INSPIRE is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    INSPIRE is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.

    In applying this licence, CERN does not waive the privileges and immunities
    granted to it by virtue of its status as an Intergovernmental Organization
    or submit itself to any jurisdiction.


API Docs
========

Tasks API
---------
.. autotask:: inspire_crawler.tasks.schedule_crawl(spider, workflow, **kwargs)
.. autotask:: inspire_crawler.tasks.submit_results(job_id, errors, log_file, results_uri, results_data=None)


Signal receivers
----------------
.. automodule:: inspire_crawler.receivers
    :members: receive_oaiharvest_job
    :undoc-members:


Configuration
-------------
.. automodule:: inspire_crawler.config
    :members:
    :undoc-members:


Models
------
.. automodule:: inspire_crawler.models
    :members:
    :undoc-members:


Errors
------
.. automodule:: inspire_crawler.errors
    :members:
    :undoc-members:
