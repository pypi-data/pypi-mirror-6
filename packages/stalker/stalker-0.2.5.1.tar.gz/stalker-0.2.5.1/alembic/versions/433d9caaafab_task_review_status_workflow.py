"""task review/status workflow

Revision ID: 433d9caaafab
Revises: 46775e4a3d96
Create Date: 2014-01-31 01:51:08.457109

"""

# revision identifiers, used by Alembic.
revision = '433d9caaafab'
down_revision = '46775e4a3d96'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    # Enum Types
    time_unit_enum = postgresql.ENUM(
        'min', 'h', 'd', 'w', 'm', 'y',
        name='TimeUnit',
        create_type=False
    )
    review_schedule_model_enum = postgresql.ENUM(
        'effort', 'length', 'duration',
        name='ReviewScheduleModel',
        create_type=False
    )

    task_dependency_target_enum = postgresql.ENUM(
        'onend', 'onstart',
        name='TaskDependencyTarget',
        create_type=False
    )

    task_dependency_gap_model = postgresql.ENUM(
        'length', 'duration',
        name='TaskDependencyGapModel',
        create_type=False
    )

    resource_allocation_strategy_enum = postgresql.ENUM(
        'minallocated', 'maxloaded', 'minloaded', 'order', 'random',
        name='ResourceAllocationStrategy',
        create_type=False
    )

    # Reviews
    op.create_table(
        'Reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('reviewer_id', sa.Integer(), nullable=False),
        sa.Column('_review_number', sa.Integer(), nullable=True),
        sa.Column('schedule_timing', sa.Float(), nullable=True),
        sa.Column('schedule_unit', time_unit_enum, nullable=False),
        sa.Column('schedule_constraint', sa.Integer(),
                  nullable=False),
        sa.Column('schedule_model', review_schedule_model_enum,
                  nullable=False),
        sa.Column('status_id', sa.Integer(), nullable=False),
        sa.Column('status_list_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['SimpleEntities.id'], ),
        sa.ForeignKeyConstraint(['reviewer_id'], ['Users.id'], ),
        sa.ForeignKeyConstraint(['status_id'], ['Statuses.id'], ),
        sa.ForeignKeyConstraint(['status_list_id'],
                                ['StatusLists.id'], ),
        sa.ForeignKeyConstraint(['task_id'], ['Tasks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Task_Responsible
    op.create_table(
        'Task_Responsible',
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('responsible_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['responsible_id'], ['Users.id']
        ),
        sa.ForeignKeyConstraint(['task_id'], ['Tasks.id']),
        sa.PrimaryKeyConstraint('task_id', 'responsible_id')
    )

    # Task_Alternative_Resources
    op.create_table(
        'Task_Alternative_Resources',
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('resource_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['resource_id'], ['Users.id'], ),
        sa.ForeignKeyConstraint(['task_id'], ['Tasks.id'], ),
        sa.PrimaryKeyConstraint('task_id', 'resource_id')
    )

    # Task Computed Resources
    op.create_table(
        'Task_Computed_Resources',
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('resource_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['resource_id'], ['Users.id'], ),
        sa.ForeignKeyConstraint(['task_id'], ['Tasks.id'], ),
        sa.PrimaryKeyConstraint('task_id', 'resource_id')
    )

    # EntityTypes
    op.add_column(
        u'EntityTypes',
        sa.Column('dateable', sa.Boolean(), nullable=True)
    )

    # Projects
    op.drop_column(u'Projects', 'timing_resolution')

    # Studios
    op.add_column(
        u'Studios',
        sa.Column('is_scheduling', sa.Boolean(), nullable=True)
    )
    op.add_column(
        u'Studios',
        sa.Column('is_scheduling_by_id', sa.Integer(), nullable=True)
    )
    op.add_column(
        u'Studios',
        sa.Column('last_schedule_message', sa.PickleType(), nullable=True)
    )
    op.add_column(
        u'Studios',
        sa.Column('last_scheduled_at', sa.DateTime(), nullable=True)
    )
    op.add_column(
        u'Studios',
        sa.Column('last_scheduled_by_id', sa.Integer(), nullable=True)
    )
    op.add_column(
        u'Studios',
        sa.Column('scheduling_started_at', sa.DateTime(), nullable=True)
    )
    op.drop_column(u'Studios', 'daily_working_hours')

    # Task Dependencies

    # *************************************************************************
    # dependency_target - onend by default
    op.add_column(
        u'Task_Dependencies',
        sa.Column(
            'dependency_target',
            task_dependency_target_enum,
            nullable=True
        )
    )
    # fill data
    op.execute("""
        UPDATE
           "Task_Dependencies"
        SET
            dependency_target = 'onend'
    """)

    # alter column to be nullable false
    op.alter_column(
        u'Task_Dependencies',
        'dependency_target',
        existing_nullable=True,
        nullable=False
    )
    # *************************************************************************

    op.alter_column(
        u'Task_Dependencies',
        'depends_to_task_id',
        new_column_name='depends_to_id'
    )

    # *************************************************************************
    # gap_constraint column - 0 by default
    op.add_column(
        u'Task_Dependencies',
        sa.Column('gap_constraint', sa.Integer(), nullable=True)
    )
    # fill data
    op.execute("""
        UPDATE
           "Task_Dependencies"
        SET
            gap_constraint = 0
    """)

    # alter column to be nullable false
    op.alter_column(
        u'Task_Dependencies',
        'gap_constraint',
        existing_nullable=True,
        nullable=False
    )
    # *************************************************************************

    # *************************************************************************
    # gap_model - length by default
    op.add_column(
        u'Task_Dependencies',
        sa.Column(
            'gap_model', task_dependency_gap_model,
            nullable=True
        )
    )
    # fill data
    op.execute("""
        UPDATE
           "Task_Dependencies"
        SET
            gap_model = 'length'
    """)

    # alter column to be nullable false
    op.alter_column(
        u'Task_Dependencies',
        'gap_model',
        existing_nullable=True,
        nullable=False
    )
    # *************************************************************************

    # *************************************************************************
    # gap_timing - 0 by default
    op.add_column(
        u'Task_Dependencies',
        sa.Column('gap_timing', sa.Float(), nullable=True)
    )
    op.add_column(
        u'Task_Dependencies',
        sa.Column(
            'gap_unit', time_unit_enum,
            nullable=True
        )
    )
    # fill data
    op.execute("""
        UPDATE
           "Task_Dependencies"
        SET
            gap_timing = 0
    """)

    # alter column to be nullable false
    op.alter_column(
        u'Task_Dependencies',
        'gap_timing',
        existing_nullable=True,
        nullable=False
    )
    # *************************************************************************

    # Tasks
    op.add_column(
        u'Tasks',
        sa.Column('_review_number', sa.Integer(), nullable=True)
    )

    # *************************************************************************
    # allocation_strategy - minallocated by default
    op.add_column(
        u'Tasks',
        sa.Column(
            'allocation_strategy',
            resource_allocation_strategy_enum,
            nullable=True
        )
    )
    # fill data
    op.execute("""
        UPDATE
           "Tasks"
        SET
            allocation_strategy = 'minallocated'
    """)

    # alter column to be nullable false
    op.alter_column(
        u'Tasks',
        'allocation_strategy',
        existing_nullable=True,
        nullable=False
    )
    # *************************************************************************

    # *************************************************************************
    # persistent_allocation - True by default
    op.add_column(
        u'Tasks',
        sa.Column('persistent_allocation', sa.Boolean(), nullable=True)
    )
    # fill data
    op.execute("""
        UPDATE
           "Tasks"
        SET
            persistent_allocation = TRUE
    """)

    # alter column to be nullable false
    op.alter_column(
        u'Tasks',
        'persistent_allocation',
        existing_nullable=True,
        nullable=False
    )
    # *************************************************************************

    op.drop_column(u'Tasks', 'timing_resolution')

    op.drop_column(u'TimeLogs', 'timing_resolution')
    op.create_unique_constraint(None, 'Users', ['login'])

    op.drop_column(u'Vacations', 'timing_resolution')

    # before dropping responsible_id column from the Tasks table
    # move the data to the Task_Responsible table
    op.execute(
        'insert into "Task_Responsible" '
        '   select id, responsible_id '
        '   from "Tasks" where responsible_id is not NULL'
    )

    # now drop the data
    op.drop_column(u'Tasks', 'responsible_id')


def downgrade():
    """downgrade
    """
    op.add_column(
        u'Vacations',
        sa.Column('timing_resolution', postgresql.INTERVAL(), nullable=True)
    )
    #op.drop_constraint(None, 'Users')
    op.add_column(
        u'TimeLogs',
        sa.Column('timing_resolution', postgresql.INTERVAL(), nullable=True)
    )
    op.add_column(
        u'Tasks',
        sa.Column('responsible_id', sa.INTEGER(), nullable=True)
    )

    # restore data
    op.execute("""
        UPDATE
           "Tasks"
        SET
            responsible_id = t2.responsible_id
        FROM (
            SELECT task_id, responsible_id
            FROM "Task_Responsible"
        ) as t2
        WHERE "Tasks".id = t2.task_id
    """)

    op.add_column(
        u'Tasks',
        sa.Column('timing_resolution', postgresql.INTERVAL(), nullable=True)
    )
    op.drop_column(u'Tasks', 'persistent_allocation')
    op.drop_column(u'Tasks', 'allocation_strategy')
    op.drop_column(u'Tasks', '_review_number')
    op.alter_column(
        u'Task_Dependencies',
        'depends_to_id',
        new_column_name='depends_to_task_id'
    )
    op.drop_column(u'Task_Dependencies', 'gap_unit')
    op.drop_column(u'Task_Dependencies', 'gap_timing')
    op.drop_column(u'Task_Dependencies', 'gap_model')
    op.drop_column(u'Task_Dependencies', 'gap_constraint')
    op.drop_column(u'Task_Dependencies', 'dependency_target')
    op.add_column(
        u'Studios',
        sa.Column('daily_working_hours', sa.INTEGER(), nullable=True)
    )
    op.drop_column(u'Studios', 'scheduling_started_at')
    op.drop_column(u'Studios', 'last_scheduled_by_id')
    op.drop_column(u'Studios', 'last_scheduled_at')
    op.drop_column(u'Studios', 'last_schedule_message')
    op.drop_column(u'Studios', 'is_scheduling_by_id')
    op.drop_column(u'Studios', 'is_scheduling')
    op.add_column(
        u'Projects',
        sa.Column('timing_resolution', postgresql.INTERVAL(), nullable=True)
    )
    op.drop_column(u'EntityTypes', 'dateable')
    op.drop_table('Task_Alternative_Resources')
    op.drop_table('Task_Computed_Resources')
    op.drop_table('Reviews')
    # will loose all the responsible data, change if you care!
    op.drop_table('Task_Responsible')
