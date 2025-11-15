"""Add authentication fields to usuarios only

Revision ID: 04c005510a3f
Revises:
Create Date: 2025-09-16 17:43:27.024464

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "04c005510a3f"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add authentication fields to usuarios table
    op.add_column(
        "usuarios", sa.Column("nombre_usuario", sa.String(length=50), nullable=True)
    )
    op.add_column(
        "usuarios", sa.Column("contrasena_hash", sa.String(length=255), nullable=True)
    )
    op.add_column("usuarios", sa.Column("es_admin", sa.Boolean(), nullable=True))

    # Create index for nombre_usuario
    op.create_index(
        op.f("ix_usuarios_nombre_usuario"), "usuarios", ["nombre_usuario"], unique=True
    )


def downgrade() -> None:
    # Remove authentication fields from usuarios table
    op.drop_index(op.f("ix_usuarios_nombre_usuario"), table_name="usuarios")
    op.drop_column("usuarios", "es_admin")
    op.drop_column("usuarios", "contrasena_hash")
    op.drop_column("usuarios", "nombre_usuario")
