# jokes_app/models.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    Boolean,
    ForeignKey,
    DateTime,
    Table,
)
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid

# Import Base from your main module (you already expose Base there)
from jokes_app.main import Base


# Bridge table: many-to-many between jokes and labels
bridge_joke_label = Table(
    "bridge_joke_label",
    Base.metadata,
    Column("joke_id", Integer, ForeignKey("fact_jokes.id", ondelete="CASCADE"), primary_key=True),
    Column("label_id", Integer, ForeignKey("dim_label.id", ondelete="CASCADE"), primary_key=True),
)


# -----------------------
# Dimension tables
# -----------------------

class DimLanguage(Base):
    __tablename__ = "dim_language"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(8), nullable=False, unique=True)  # "en", "de"
    name = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DimJokeType(Base):
    __tablename__ = "dim_joke_type"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(32), nullable=False, unique=True)  # "single", "twopart"
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DimLabel(Base):
    __tablename__ = "dim_label"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), nullable=False, unique=True)  # "pun", "dark", etc.
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DimSource(Base):
    __tablename__ = "dim_source"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False, unique=True)  # "JokeAPI", "Local", "Reddit"
    url = Column(String(512), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DimUser(Base):
    __tablename__ = "dim_user"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(128), nullable=True)
    email = Column(String(256), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DimSession(Base):
    __tablename__ = "dim_session"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("dim_user.id"), nullable=True)
    user_agent = Column(String(512), nullable=True)
    ip_address = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# -----------------------
# Fact tables
# -----------------------

class FactJokes(Base):
    __tablename__ = "fact_jokes"

    id = Column(Integer, primary_key=True, index=True)
    joke_type_id = Column(Integer, ForeignKey("dim_joke_type.id"), nullable=False)
    language_id = Column(Integer, ForeignKey("dim_language.id"), nullable=False)
    source_id = Column(Integer, ForeignKey("dim_source.id"), nullable=True)

    # Text fields: either single (joke_text) or twopart (setup/delivery)
    joke_text = Column(Text, nullable=True)
    setup = Column(Text, nullable=True)
    delivery = Column(Text, nullable=True)

    # moderation & bookkeeping
    is_active = Column(Boolean, nullable=False, server_default="true")
    is_flagged = Column(Boolean, nullable=False, server_default="false")

    # optional linkage to an upload/session
    upload_session_id = Column(UUID(as_uuid=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class FactRatings(Base):
    __tablename__ = "fact_ratings"

    id = Column(Integer, primary_key=True, index=True)
    joke_id = Column(Integer, ForeignKey("fact_jokes.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(UUID(as_uuid=True), ForeignKey("dim_session.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("dim_user.id"), nullable=True)

    rating = Column(Float, nullable=False)  # 1.0 - 5.0
    comment = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


# (Optional) convenience relationships can be added later (SQLAlchemy ORM relationships)
