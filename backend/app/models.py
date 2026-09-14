from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

class Document(Base):
    __tablename__="documents"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index = True
    )

    filename: Mapped[str]= mapped_column(
        String(255)
    )

    content: Mapped[str] = mapped_column(
        Text()
    )