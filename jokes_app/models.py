from sqlalchemy import Column, Integer, String, Text, Boolean, Float, ForeignKey, DateTime, Table
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from jokes_app.database import Base

# Bridge table
joke_labels = Table(
    "joke_labels",
    Base.metadata,
    Column("joke_id", Integer, ForeignKey("fact_jokes.id", ondelete="CASCADE"), primary_key=True),
    Column("label_id", Integer, ForeignKey("dim_label.id", ondelete="CASCADE"), primary_key=True),
)

# Dimensions
class DimJokeType(Base):
    __tablename__ = "dim_joke_type"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DimLanguage(Base):
    __tablename__ = "dim_language"
    id = Column(Integer, primary_key=True)
    code = Column(String(5), unique=True, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DimLabel(Base):
    __tablename__ = "dim_label"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DimSession(Base):
    __tablename__ = "dim_session"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DimRating(Base):
    __tablename__ = "dim_rating"
    id = Column(Integer, primary_key=True)
    score = Column(Float, nullable=False)
    description = Column(String, nullable=True)

class DimSource(Base):
    __tablename__ = "dim_source"
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Fact table
class FactJokes(Base):
    __tablename__ = "fact_jokes"
    id = Column(Integer, primary_key=True)
    joke_type_id = Column(Integer, ForeignKey("dim_joke_type.id"), nullable=False)
    language_id = Column(Integer, ForeignKey("dim_language.id"), nullable=False)
    session_id = Column(UUID(as_uuid=True), ForeignKey("dim_session.id"), nullable=True)
    rating_id = Column(Integer, ForeignKey("dim_rating.id"), nullable=True)

    joke_text = Column(Text, nullable=True)
    setup = Column(Text, nullable=True)
    delivery = Column(Text, nullable=True)

    is_active = Column(Boolean, nullable=False, server_default="true")
    is_flagged = Column(Boolean, nullable=False, server_default="false")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    joke_type = relationship("DimJokeType", backref="jokes")
    language = relationship("DimLanguage", backref="jokes")
    labels = relationship("DimLabel", secondary=joke_labels, backref="jokes")
