"""Create laboratory equipment inventory."""

from alembic import op
import sqlalchemy as sa

revision = "0001_equipment"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "equipment",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("category", sa.String(60), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("low_stock_threshold", sa.Integer(), nullable=False),
        sa.Column("location", sa.String(120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("quantity >= 0", name="ck_equipment_quantity"),
        sa.CheckConstraint("low_stock_threshold >= 0", name="ck_equipment_threshold"),
    )
    op.create_index("ix_equipment_category", "equipment", ["category"])


def downgrade():
    op.drop_index("ix_equipment_category", table_name="equipment")
    op.drop_table("equipment")
