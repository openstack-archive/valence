#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Add node.clean_step

Revision ID: 4f399b21ae71
Revises: 1e1d5ace7dc6
Create Date: 2015-02-18 01:21:46.062311

"""

# revision identifiers, used by Alembic.
revision = '4f399b21ae71'
down_revision = '1e1d5ace7dc6'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('nodes', sa.Column('clean_step', sa.Text(),
                  nullable=True))


def downgrade():
    op.drop_column('nodes', 'clean_step')
