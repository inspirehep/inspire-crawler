# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2017 CERN.
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
"""Create inspire_crawler tables."""

from __future__ import absolute_import, print_function

import pytest
from sqlalchemy import inspect

from invenio_db.utils import drop_alembic_version_table


def test_alembic_revision_34b150f80576(app, db):
    ext = app.extensions['invenio-db']

    if db.engine.name == 'sqlite':
        raise pytest.skip('Upgrades are not supported on SQLite.')

    db.drop_all()
    drop_alembic_version_table()

    with app.app_context():
        inspector = inspect(db.engine)
        assert 'crawler_job' not in inspector.get_table_names()
        assert 'crawler_workflows_object' not in inspector.get_table_names()

    ext.alembic.upgrade(target='34b150f80576')
    with app.app_context():
        inspector = inspect(db.engine)
        assert 'crawler_job' in inspector.get_table_names()
        assert 'crawler_workflows_object' in inspector.get_table_names()

    ext.alembic.downgrade(target='df8d1c51b820')
    with app.app_context():
        inspector = inspect(db.engine)
        assert 'crawler_job' not in inspector.get_table_names()
        assert 'crawler_workflows_object' not in inspector.get_table_names()

    drop_alembic_version_table()
