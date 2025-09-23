import os
from pathlib import Path

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from jokes_app.database import get_db
from jokes_app.models import DimLanguage, DimJokeType, FactJokes

import logging



# -------------------------------
# ENV + LOGGING
# -------------------------------
load_dotenv()
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

TESTING = os.getenv("TESTING", "false").lower() == "true"

# -------------------------------
# APP SETUP
# -------------------------------
app = FastAPI(title="Random Joke App")
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

router = APIRouter()

# -------------------------------
# ROUTES
# -------------------------------


@app.get("/", response_class=HTMLResponse)
async def read_main(request: Request):
    """Render homepage with template."""
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/joke", response_class=JSONResponse)
async def get_joke(
    lang: str = "en",
    blacklist: str = "",
    db: AsyncSession = Depends(get_db),
):
    """Fetch a joke from DB or external API."""
    # Validate language
    supported_langs = {"cs": "Czech", "de": "German", "en": "English", "es": "Spanish", "fr": "French"}
    if lang not in supported_langs:
        lang = "en"

    # Step 1: Try to fetch from DB
    result = await db.execute(
        select(FactJokes).options(selectinload(FactJokes.joke_type)).limit(1)
    )
    joke = result.scalar_one_or_none()

    logger.debug("TESTING=%s, joke_from_db=%s", TESTING, joke)

    if joke:
        joke_type_name = joke.joke_type.name if joke.joke_type else "twopart"
        if joke_type_name == "single":
            return {"type": "single", "joke": joke.joke_text or ""}
        return {"type": "twopart", "setup": joke.setup, "delivery": joke.delivery}

    # Step 2: If TESTING, fail early
    if TESTING:
        raise HTTPException(status_code=404, detail="No jokes found in test mode")

    # Step 3: Fetch from external JokeAPI
    url = f"https://v2.jokeapi.dev/joke/Any?lang={lang}"
    if blacklist:
        url += f"&blacklistFlags={blacklist}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(url)
            res.raise_for_status()
            data = res.json()
    except Exception as e:
        logger.error("Error fetching joke from API: %s", e)
        raise HTTPException(status_code=502, detail="Error fetching joke from API")

    # Step 4: Extract joke data
    joke_type_name = data.get("type", "single")
    joke_text = data.get("joke")
    setup = data.get("setup")
    delivery = data.get("delivery")

    # Step 5: Upsert dimensions
    joke_type = await db.execute(select(DimJokeType).where(DimJokeType.name == joke_type_name))
    joke_type_obj = joke_type.scalar_one_or_none()
    if not joke_type_obj:
        joke_type_obj = DimJokeType(name=joke_type_name)
        db.add(joke_type_obj)
        await db.flush()

    language = await db.execute(select(DimLanguage).where(DimLanguage.code == lang))
    language_obj = language.scalar_one_or_none()
    if not language_obj:
        language_obj = DimLanguage(code=lang, name=supported_langs.get(lang, lang))
        db.add(language_obj)
        await db.flush()

    # Step 6: Insert joke
    new_joke = FactJokes(
        joke_type_id=joke_type_obj.id,
        language_id=language_obj.id,
        joke_text=joke_text,
        setup=setup,
        delivery=delivery,
        is_active=True,
        is_flagged=False,
    )
    db.add(new_joke)
    await db.commit()

    # Step 7: Return joke
    if joke_type_name == "single":
        return {"type": "single", "joke": joke_text}
    return {"type": "twopart", "setup": setup, "delivery": delivery}


# -------------------------------
# REGISTER ROUTER
# -------------------------------
app.include_router(router)
