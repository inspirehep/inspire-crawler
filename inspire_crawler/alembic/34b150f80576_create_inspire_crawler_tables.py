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

from alembic import op
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy_utils.types import ChoiceType, UUIDType

from inspire_crawler.models import JobStatus

# revision identifiers, used by Alembic.
revision = '34b150f80576'
down_revision = 'df8d1c51b820'
branch_labels = ()
depends_on = 'a26f133d42a9'


def upgrade():
    """Upgrade database."""
    op.create_table(
        'crawler_job',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('job_id', UUIDType, index=True),
        sa.Column('spider', sa.String(255), index=True),
        sa.Column('workflow', sa.String(255), index=True),
        sa.Column('results', sa.Text, nullable=True),
        sa.Column(
            'status',
            ChoiceType(JobStatus, impl=sa.String(10)),
            nullable=False
        ),
        sa.Column('logs', sa.Text, nullable=True),
        sa.Column(
            'scheduled',
            sa.DateTime,
            default=datetime.now,
            nullable=False,
            index=True
        )
    )

    op.create_table(
        'crawler_workflows_object',
        sa.Column('job_id', UUIDType, primary_key=True),
        sa.Column(
            'object_id',
            sa.Integer,
            sa.ForeignKey(
                'workflows_object.id',
                ondelete="CASCADE",
                onupdate="CASCADE",
            ),
            primary_key=True
        )
    )


def downgrade():
    """Downgrade database."""
    op.drop_table('crawler_job')
    op.drop_table('crawler_workflows_object')
