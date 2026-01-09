from typing import Sequence, Union
from alembic import op


revision: str = "257f88caae50"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        "CREATE TABLE IF NOT EXISTS multi_baker ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "model TEXT NOT NULL UNIQUE);"
    )
    op.execute(
        "CREATE TABLE IF NOT EXISTS panel ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "panel TEXT NOT NULL UNIQUE);"
    )
    op.execute(
        "CREATE TABLE IF NOT EXISTS model_panel ("
        "model_id INTEGER NOT NULL, "
        "panel_id INTEGER NOT NULL,"
        "PRIMARY KEY (model_id, panel_id)"
        "FOREIGN KEY (model_id) REFERENCES multi_baker(id),"
        "FOREIGN KEY (panel_id) REFERENCES panel(id));"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(""" DROP TABLE multi_baker """)
    op.execute(""" DROP TABLE panel """)
    op.execute(""" DROP TABLE model_panel """)
