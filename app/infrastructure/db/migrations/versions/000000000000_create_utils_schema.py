"""Create utils schema migration

Revision ID: 000000000000
Revises: 
Create Date: 2024-01-09 21:50:03.369562

"""
from alembic import op
from sqlalchemy.schema import CreateSchema, DropSchema

# revision identifiers, used by Alembic.
revision = "000000000000"
down_revision = None
branch_labels = None
depends_on = None

schema = "utils"


def upgrade() -> None:
    connection = op.get_bind()
    if not connection.dialect.has_schema(connection, schema):
        connection.execute(CreateSchema(schema))


def downgrade() -> None:
    connection = op.get_bind()
    if connection.dialect.has_schema(connection, schema):
        connection.execute(DropSchema(schema))
