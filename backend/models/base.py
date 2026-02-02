from app.extensions import db
import uuid
from datetime import datetime, timezone
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column


def get_uuid_type():
    """Return a UUID-compatible type for MySQL (CHAR(36))."""
    return sa.String(36)


class BaseModel(db.Model):
    __abstract__ = True

    id: Mapped[str] = mapped_column(
        get_uuid_type(),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    
    # We will define timestamps in specific models if they differ, 
    # but many share created_at/updated_at pattern. 
    # The requirements use 'criado_em' and 'atualizado_em'.
    # I will stick to English attribute names as requested: created_at, updated_at.
