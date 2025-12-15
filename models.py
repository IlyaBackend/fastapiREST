from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Essence(Base):
    __tablename__ = 'essence'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    quantity: Mapped[int] = mapped_column(Integer)
    is_done: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
