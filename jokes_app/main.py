# jokes_app/main.py

from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
from pathlib import Path
import os
import logging

# SQLAlchemy async setup
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Table, select
from datetime import datetime

from dotenv import load_dotenv

# -------------------------------
# ENV + LOGGING SETUP
# -------------------------------
load_dotenv()  # load variables from .env
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------------
# CREATE THE APP
# -------------------------------
app = FastAPI(title="Random Joke App")

# -------------------------------
# DEFINE IMPORTANT FOLDERS
# -------------------------------
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# -------------------------------
# DATABASE CONFIG (Supabase / Postgres)
# -------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set. Please define it in your .env file.")

engine = create_async_engine(DATABASE_URL, echo=True, future=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

# -------------------------------
# STAR SCHEMA MODELS
# -------------------------------

# Many-to-many bridge table: jokes ↔ labels
joke_label_table = Table(
    "joke_labels",
    Base.metadata,
    Column("joke_id", ForeignKey("fact_jokes.id"), primary_key=True),
    Column("label_id", ForeignKey("dim_label.id"), primary_key=True)
)

class DimJokeType(Base):
    __tablename__ = "dim_joke_type"
    id = Column(Integer, primary_key=True)
    type_name = Column(String, unique=True, nullable=False)

class DimLanguage(Base):
    __tablename__ = "dim_language"
    id = Column(Integer, primary_key=True)
    language_code = Column(String(5), unique=True, nullable=False)
    language_name = Column(String, nullable=False)

class DimLabel(Base):
    __tablename__ = "dim_label"
    id = Column(Integer, primary_key=True)
    label_name = Column(String, unique=True, nullable=False)

class DimSession(Base):
    __tablename__ = "dim_session"
    id = Column(Integer, primary_key=True)
    session_token = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class DimRating(Base):
    __tablename__ = "dim_rating"
    id = Column(Integer, primary_key=True)
    score = Column(Float, nullable=False)
    description = Column(String, nullable=True)

class FactJoke(Base):
    __tablename__ = "fact_jokes"
    id = Column(Integer, primary_key=True)
    type_id = Column(Integer, ForeignKey("dim_joke_type.id"))
    language_id = Column(Integer, ForeignKey("dim_language.id"))
    session_id = Column(Integer, ForeignKey("dim_session.id"), nullable=True)
    rating_id = Column(Integer, ForeignKey("dim_rating.id"), nullable=True)

    setup = Column(Text, nullable=True)
    delivery = Column(Text, nullable=True)
    joke_text = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    labels = relationship("DimLabel", secondary=joke_label_table, backref="jokes")
    type = relationship("DimJokeType")
    language = relationship("DimLanguage")
    session = relationship("DimSession")
    rating = relationship("DimRating")

# -------------------------------
# Dependency: get DB session
# -------------------------------
async def get_db():
    async with async_session() as session:
        yield session

# -------------------------------
# ROUTES
# -------------------------------

# ROUTE 1: Homepage
@app.get("/", response_class=HTMLResponse)
async def read_main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ROUTE 2: Joke endpoint
@app.get("/joke", response_class=JSONResponse)
async def get_joke(
    lang: str = "en",
    blacklist: str = "",
    session_token: str = None,
    rating_score: float = None,
    rating_description: str = None,
    db: AsyncSession = Depends(get_db)
):
    if lang not in ["cs", "de", "en", "es", "fr"]:
        lang = "en"

    url = f"https://v2.jokeapi.dev/joke/Any?lang={lang}"
    if blacklist:
        url += f"&blacklistFlags={blacklist}"

    async with httpx.AsyncClient() as client:
        res = await client.get(url)
        data = res.json()

    joke_type_name = data.get("type", "single")
    setup = data.get("setup")
    delivery = data.get("delivery")
    joke_text = data.get("joke")
    labels = list(data.get("flags", {}).keys()) if isinstance(data.get("flags"), dict) else []

    # ✅ Only include labels where the flag is true
    flags = data.get("flags", {})
    labels = [name for name, value in flags.items() if value is True]

    # -------------------------------
    # 1️⃣ Integrity check
    # -------------------------------
    stmt = select(FactJoke)
    if joke_type_name == "single":
        stmt = stmt.where(FactJoke.joke_text == joke_text)
    else:
        stmt = stmt.where(FactJoke.setup == setup, FactJoke.delivery == delivery)

    existing = await db.execute(stmt)
    if existing.scalar_one_or_none():
        return {"message": "Joke already exists", "joke": data}

    # -------------------------------
    # 2️⃣ Upsert dimensions
    # -------------------------------
    # Joke type
    result = await db.execute(select(DimJokeType).where(DimJokeType.type_name == joke_type_name))
    joke_type = result.scalar_one_or_none()
    if not joke_type:
        joke_type = DimJokeType(type_name=joke_type_name)
        db.add(joke_type)
        await db.flush()

    # Language
    result = await db.execute(select(DimLanguage).where(DimLanguage.language_code == lang))
    language = result.scalar_one_or_none()
    if not language:
        language = DimLanguage(language_code=lang, language_name=lang)
        db.add(language)
        await db.flush()

    # Labels
    label_objs = []
    for label_name in labels:
        result = await db.execute(select(DimLabel).where(DimLabel.label_name == label_name))
        label_obj = result.scalar_one_or_none()
        if not label_obj:
            label_obj = DimLabel(label_name=label_name)
            db.add(label_obj)
            await db.flush()
        label_objs.append(label_obj)

    # Session
    session_obj = None
    if session_token:
        result = await db.execute(select(DimSession).where(DimSession.session_token == session_token))
        session_obj = result.scalar_one_or_none()
        if not session_obj:
            session_obj = DimSession(session_token=session_token)
            db.add(session_obj)
            await db.flush()

    # Rating
    rating_obj = None
    if rating_score is not None:
        rating_obj = DimRating(score=rating_score, description=rating_description)
        db.add(rating_obj)
        await db.flush()

    # -------------------------------
    # 3️⃣ Insert fact joke
    # -------------------------------
    new_joke = FactJoke(
        type_id=joke_type.id,
        language_id=language.id,
        setup=setup,
        delivery=delivery,
        joke_text=joke_text,
        labels=label_objs,
        session_id=session_obj.id if session_obj else None,
        rating_id=rating_obj.id if rating_obj else None
    )
    db.add(new_joke)
    await db.commit()
    logger.info(f"Inserted new joke with ID {new_joke.id}")

    return {"message": "New joke added", "joke": data}


# -------------------------------
# ROUTE 3: Optional endpoint for all jokes
# -------------------------------
@app.get("/jokes", response_class=JSONResponse)
async def list_jokes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FactJoke))
    jokes = result.scalars().all()

    return {
        "jokes": [
            {
                "id": j.id,
                "setup": j.setup,
                "delivery": j.delivery,
                "joke_text": j.joke_text,
                "type": j.type.type_name if j.type else None,
                "language": j.language.language_code if j.language else None,
                "labels": [lbl.label_name for lbl in j.labels],
                "rating": {
                    "score": j.rating.score,
                    "description": j.rating.description
                } if j.rating else None
            }
            for j in jokes
        ]
    }
