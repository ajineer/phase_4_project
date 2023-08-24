"""creating list, calendar, and task tables

Revision ID: 2a35f1bf593a
Revises: 959028127816
Create Date: 2023-08-24 15:29:57.428716

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2a35f1bf593a'
down_revision = '959028127816'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('calendars',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('year', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_calendars_user_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('events',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('start', sa.Time(), nullable=False),
    sa.Column('end', sa.Time(), nullable=False),
    sa.Column('calendar_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['calendar_id'], ['calendars.id'], name=op.f('fk_events_calendar_id_calendars'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('lists',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('event_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['event_id'], ['events.id'], name=op.f('fk_lists_event_id_events'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_lists_user_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('tasks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('list_id', sa.Integer(), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('status', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['list_id'], ['lists.id'], name=op.f('fk_tasks_list_id_lists'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tasks')
    op.drop_table('lists')
    op.drop_table('events')
    op.drop_table('calendars')
    # ### end Alembic commands ###
