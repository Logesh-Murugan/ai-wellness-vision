"""Alembic migration — add family_members table + family_member_id FK on analysis_records."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "add_family_001"
down_revision = None  # TODO: set to your latest revision ID before running
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Create enum type (idempotent)
    conn = op.get_bind()
    conn.execute(sa.text(
        "DO $$ BEGIN "
        "CREATE TYPE familyrelationship AS ENUM "
        "('self','father','mother','spouse','sibling','child','other'); "
        "EXCEPTION WHEN duplicate_object THEN NULL; END $$"
    ))

    # 2. family_members table
    op.create_table(
        "family_members",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "owner_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column(
            "relationship",
            sa.Enum(
                "self", "father", "mother", "spouse", "sibling", "child", "other",
                name="familyrelationship",
                create_type=False,
            ),
            nullable=False,
            server_default="other",
        ),
        sa.Column("age", sa.Integer, nullable=True),
        sa.Column(
            "language_preference",
            sa.String(10),
            nullable=False,
            server_default="en",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_family_members_owner_user_id", "family_members", ["owner_user_id"])

    # 3. Add nullable FK column on analysis_records
    op.add_column(
        "analysis_records",
        sa.Column(
            "family_member_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("family_members.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_analysis_records_family_member_id",
        "analysis_records",
        ["family_member_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_analysis_records_family_member_id", table_name="analysis_records")
    op.drop_column("analysis_records", "family_member_id")
    op.drop_index("ix_family_members_owner_user_id", table_name="family_members")
    op.drop_table("family_members")
    op.execute("DROP TYPE IF EXISTS familyrelationship")