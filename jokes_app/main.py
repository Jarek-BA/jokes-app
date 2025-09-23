# jokes_app/main.py

import os
import logging
from pathlib import Path
import httpx

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload
from sqlalchemy import select, and_

from dotenv import load_dotenv

# jokes_app/main.py
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from jokes_app.database import engine, async_session  # <- Base not needed here
from jokes_app.models import FactJokes, DimJokeType, DimLanguage, DimLabel

# Import models
from jokes_app.models import (
    DimLanguage,
    DimJokeType,
    DimLabel,
    FactJokes
)

# -------------------------------
# ENV + LOGGING
# -------------------------------
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------------
# APP SETUP
# -------------------------------
app = FastAPI(title="Random Joke App")
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# -------------------------------
# DATABASE CONFIG
# -------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in .env")

engine = create_async_engine(DATABASE_URL, echo=True, future=True)
async_session = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

# Dependency
from typing import AsyncGenerator

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

# -------------------------------
# ROUTES
# -------------------------------

# Homepage
@app.get("/", response_class=HTMLResponse)
async def read_main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Fetch joke endpoint
@app.get("/joke", response_class=JSONResponse)
async def get_joke(
    lang: str = "en",
    blacklist: str = "",
    session_token: str | None = None,
    rating_score: float | None = None,
    rating_description: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    # Validate language
    if lang not in ["cs", "de", "en", "es", "fr"]:
        lang = "en"

    # Build JokeAPI URL
    url = f"https://v2.jokeapi.dev/joke/Any?lang={lang}"
    if blacklist:
        url += f"&blacklistFlags={blacklist}"

    # Fetch joke from API
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(url)
            res.raise_for_status()
            data = res.json()
            logger.info(f"HTTP Status: {res.status_code}")
    except httpx.RequestError as e:
        logger.error(f"HTTP request failed: {e}")
        return {"message": "Error fetching joke from API"}
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP status error: {e}")
        return {"message": "Error fetching joke from API"}

    joke_type_name = data.get("type", "single")
    joke_text = data.get("joke")
    setup = data.get("setup")
    delivery = data.get("delivery")

    # Only include labels where flag is True
    flags = data.get("flags", {})
    labels = [name for name, value in flags.items() if value is True]

    # -------------------------------
    # 1️⃣ Check if joke already exists
    # -------------------------------
    try:
        stmt = select(FactJokes)
        if joke_type_name == "single":
            stmt = stmt.where(FactJokes.joke_text == joke_text)
        else:
            stmt = stmt.where(and_(FactJokes.setup == setup, FactJokes.delivery == delivery))
        existing = await db.execute(stmt)
        if existing.scalar_one_or_none():
            return {"message": "Joke already exists", "joke": data}
    except Exception as e:
        logger.error(f"Integrity check failed: {e}")

    # -------------------------------
    # 2️⃣ Upsert dimensions (safely)
    # -------------------------------
    joke_type = None
    language = None
    label_objs = []

    try:
        # Joke type
        result = await db.execute(select(DimJokeType).where(DimJokeType.name == joke_type_name))
        joke_type = result.scalar_one_or_none()
        if not joke_type:
            joke_type = DimJokeType(name=joke_type_name)
            db.add(joke_type)
            await db.flush()

        # Language
        result = await db.execute(select(DimLanguage).where(DimLanguage.code == lang))
        language = result.scalar_one_or_none()
        if not language:
            language = DimLanguage(code=lang, name=lang)
            db.add(language)
            await db.flush()

        # Labels
        for label_name in labels:
            result = await db.execute(select(DimLabel).where(DimLabel.name == label_name))
            label_obj = result.scalar_one_or_none()
            if not label_obj:
                label_obj = DimLabel(name=label_name)
                db.add(label_obj)
                await db.flush()
            label_objs.append(label_obj)

    except Exception as e:
        logger.error(f"Upserting dimensions failed: {e}")
        await db.rollback()
        return {"message": "Error processing joke dimensions"}

    # -------------------------------
    # 3️⃣ Insert fact joke
    # -------------------------------
    if not joke_type or not language:
        # Safety check: required dimensions must exist
        logger.error("Required joke_type or language not found. Aborting insertion.")
        return {"message": "Cannot insert joke due to missing dimensions"}

    try:
        new_joke = FactJokes(
            joke_type_id=joke_type.id,
            language_id=language.id,
            setup=setup,
            delivery=delivery,
            joke_text=joke_text,
        )
        # Assign many-to-many labels
        new_joke.labels = label_objs

        db.add(new_joke)
        await db.commit()
        logger.info(f"Inserted new joke with ID {new_joke.id}")
    except Exception as e:
        logger.error(f"DB insert failed: {e}")
        await db.rollback()
        return {"message": "Error saving joke"}

# Optional endpoint: list all jokes
@app.get("/jokes", response_class=JSONResponse)
async def list_jokes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FactJokes).options(selectinload(FactJokes.labels)))
    jokes = result.scalars().all()

    return {
        "jokes": [
            {
                "id": j.id,
                "setup": j.setup,
                "delivery": j.delivery,
                "joke_text": j.joke_text,
                "type": j.joke_type.name if j.joke_type else None,
                "language": j.language.code if j.language else None,
                "labels": [lbl.name for lbl in j.labels],
            }
            for j in jokes
        ]
    }
