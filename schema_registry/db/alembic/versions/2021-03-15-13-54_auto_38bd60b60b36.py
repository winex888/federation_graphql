"""auto

Revision ID: 38bd60b60b36
Revises: 
Create Date: 2021-03-15 13:54:44.049550+03:00

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '38bd60b60b36'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    schema_upgrades()
    data_upgrades()


def downgrade():
    data_downgrades()
    schema_downgrades()


def schema_upgrades():
    """schema upgrade migrations go here."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('fields',
    sa.Column('id', postgresql.UUID(), nullable=False),
    sa.Column('schema_id', postgresql.UUID(), nullable=True, comment='Ссылка на схему'),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('external', sa.Boolean(), nullable=False),
    sa.Column('extend', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('not_valid_schema',
    sa.Column('validation_errors', sa.String(), nullable=True),
    sa.Column('id', postgresql.UUID(), nullable=False),
    sa.Column('service_name', sa.String(), nullable=False),
    sa.Column('port', sa.Integer(), nullable=False),
    sa.Column('host', sa.String(), nullable=False),
    sa.Column('endpoint', sa.String(), nullable=False),
    sa.Column('status', sa.Integer(), nullable=False),
    sa.Column('graphql_schema', sa.String(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('last_update', sa.DateTime(), nullable=False),
    sa.Column('deleted', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('not_valid_subscription_schema',
    sa.Column('subscription_endpoint', sa.String(), nullable=False),
    sa.Column('validation_errors', sa.String(), nullable=True),
    sa.Column('id', postgresql.UUID(), nullable=False),
    sa.Column('service_name', sa.String(), nullable=False),
    sa.Column('port', sa.Integer(), nullable=False),
    sa.Column('host', sa.String(), nullable=False),
    sa.Column('endpoint', sa.String(), nullable=False),
    sa.Column('status', sa.Integer(), nullable=False),
    sa.Column('graphql_schema', sa.String(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('last_update', sa.DateTime(), nullable=False),
    sa.Column('deleted', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('operation',
    sa.Column('id', postgresql.UUID(), nullable=False),
    sa.Column('schema_id', postgresql.UUID(), nullable=True, comment='Ссылка на схему'),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('schema',
    sa.Column('id', postgresql.UUID(), nullable=False),
    sa.Column('service_name', sa.String(), nullable=False),
    sa.Column('port', sa.Integer(), nullable=False),
    sa.Column('host', sa.String(), nullable=False),
    sa.Column('endpoint', sa.String(), nullable=False),
    sa.Column('status', sa.Integer(), nullable=False),
    sa.Column('graphql_schema', sa.String(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('last_update', sa.DateTime(), nullable=False),
    sa.Column('deleted', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('subscription_schema',
    sa.Column('subscription_endpoint', sa.String(), nullable=False),
    sa.Column('id', postgresql.UUID(), nullable=False),
    sa.Column('service_name', sa.String(), nullable=False),
    sa.Column('port', sa.Integer(), nullable=False),
    sa.Column('host', sa.String(), nullable=False),
    sa.Column('endpoint', sa.String(), nullable=False),
    sa.Column('status', sa.Integer(), nullable=False),
    sa.Column('graphql_schema', sa.String(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('last_update', sa.DateTime(), nullable=False),
    sa.Column('deleted', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    # ### end Alembic commands ###


def schema_downgrades():
    """schema downgrade migrations go here."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('subscription_schema')
    op.drop_table('schema')
    op.drop_table('operation')
    op.drop_table('not_valid_subscription_schema')
    op.drop_table('not_valid_schema')
    op.drop_table('fields')
    # ### end Alembic commands ###


def data_upgrades():
    """Add any optional data upgrade migrations here!"""
    pass


def data_downgrades():
    """Add any optional data downgrade migrations here!"""
    pass