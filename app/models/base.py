from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, TIMESTAMP, String, func

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
