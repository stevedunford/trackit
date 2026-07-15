from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


class BaseModel(db.Model):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)

    active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
