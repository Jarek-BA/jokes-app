# jokes_app/models.py
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, ForeignKey, DateTime, Table
from sqlalchemy.sql import func
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base  # <-- keep this import

# Import Base from database module
from jokes_app.database import Base

# -------------------------------
# Base declarative class
# -------------------------------
#Base = declarative_base()  # <-- must assign it here so all models can inherit from Base

# -------------------------------
# Many-to-many bridge table
# -------------------------------
bridge_joke_label = Table(
    "bridge_joke_label",
    Base.metadata,
    Column("joke_id", Integer, ForeignKey("fact_jokes.id", ondelete="CASCADE"), primary_key=True),
    Column("label_id", Integer, ForeignKey("dim_label.id", ondelete="CASCADE"), primary_key=True),
)

# -------------------------------
# Dimension tables
# -------------------------------
class DimLanguage(Base):
    __tablename__ = "dim_language"
    id = Column(Integer, primary_key=True)
    code = Column(String(8), unique=True, nullable=False)
    name = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DimJokeType(Base):
    __tablename__ = "dim_joke_type"
    id = Column(Integer, primary_key=True)
    name = Column(String(32), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DimLabel(Base):
    __tablename__ = "dim_label"
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DimSession(Base):
    __tablename__ = "dim_session"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DimSource(Base):
    __tablename__ = "dim_source"
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# -------------------------------
# Fact table
# -------------------------------
# jokes_app/models.py

from sqlalchemy.orm import relationship

class FactJokes(Base):
    __tablename__ = "fact_jokes"

    id = Column(Integer, primary_key=True, index=True)
    joke_type_id = Column(Integer, ForeignKey("dim_joke_type.id"), nullable=False)
    language_id = Column(Integer, ForeignKey("dim_language.id"), nullable=False)
    source_id = Column(Integer, ForeignKey("dim_source.id"), nullable=True)

    joke_text = Column(Text, nullable=True)
    setup = Column(Text, nullable=True)
    delivery = Column(Text, nullable=True)

    is_active = Column(Boolean, nullable=False, server_default="true")
    is_flagged = Column(Boolean, nullable=False, server_default="false")

    upload_session_id = Column(UUID(as_uuid=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # -----------------------
    # Relationships
    # -----------------------
    joke_type = relationship("DimJokeType", backref="jokes")
    language = relationship("DimLanguage", backref="jokes")
    labels = relationship("DimLabel", secondary="bridge_joke_label", backref="jokes")
