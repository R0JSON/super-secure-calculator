"""Initialize base models with UUIDs and Calculation table

Revision ID: 0001_base_models
Revises:
Create Date: 2025-10-20

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
import uuid

# revision identifiers, used by Alembic.
revision = "0001_base_models"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user",
        sa.Column("id", sa.Uuid(), primary_key=True, default=uuid.uuid4, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True, index=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, default=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("hashed_password", sa.String(), nullable=False),
    )

    op.create_table(
        "calculation",
        sa.Column("id", sa.Uuid(), primary_key=True, default=uuid.uuid4, nullable=False),
        sa.Column("result", sa.Integer(), nullable=True),
        sa.Column("operand_a", sa.Integer(), nullable=True),
        sa.Column("operand_b", sa.Integer(), nullable=True),
        sa.Column("operation", sa.String(), nullable=True),
        sa.Column("owner_id", sa.Uuid(), sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False),
    )


def downgrade():
    op.drop_table("calculation")
    op.drop_table("user")
