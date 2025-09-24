import os
import logging
from pathlib import Path

import httpx
from fastapi import FastAPI, APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from jokes_app.database import get_db
from jokes_app.models import DimLanguage, DimJokeType, FactJokes
from contextlib import asynccontextmanager
from jokes_app.database import async_session


# -------------------------------
# ENV + LOGGING
# -------------------------------

logging.basicConfig(level=logging.INFO)
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

@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    logger.info(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")

    try:
        async with async_session() as session:
            await session.execute(select(1))
        logger.info("✅ DB connection verified on startup")
    except Exception as e:
        logger.error("❌ DB connection failed on startup: %s", e)

    yield  # App runs here

    logger.info("🛑 App shutdown complete")

app = FastAPI(title="Random Joke App", lifespan=lifespan)


@app.get("/", response_class=HTMLResponse)
async def read_main(request: Request):
    """Render homepage with template."""
    return templates.TemplateResponse(request, "index.html", {"request": request})


from sqlalchemy.orm import selectinload

@router.get("/joke", response_class=JSONResponse)
async def get_joke(
    lang: str = "en",
    blacklist: str = "",
    db: AsyncSession = Depends(get_db),
):
    """Fetch a joke from DB or external API, safely handle DB failures."""
    supported_langs = {"cs": "Czech", "de": "German", "en": "English", "es": "Spanish", "fr": "French"}
    if lang not in supported_langs:
        lang = "en"

    joke = None

    # -------------------------------
    # Step 1: Try to fetch from DB
    # -------------------------------
    if db:
        try:
            result = await db.execute(
                select(FactJokes).options(selectinload(FactJokes.joke_type)).limit(1)
            )
            joke = result.scalar_one_or_none()
        except Exception as e:
            logger.warning("DB fetch failed, falling back to API: %s", e)

    # -------------------------------
    # Step 2: If joke found in DB
    # -------------------------------
    if joke:
        joke_type_name = joke.joke_type.name if joke.joke_type else "twopart"
        if joke_type_name == "single":
            return {"type": "single", "joke": joke.joke_text or ""}
        return {"type": "twopart", "setup": joke.setup, "delivery": joke.delivery}


    # -------------------------------
    # Step 3: Fetch from external API
    # -------------------------------
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

    joke_type_name = data.get("type", "single")
    joke_text = data.get("joke")
    setup = data.get("setup")
    delivery = data.get("delivery")

    # -------------------------------
    # Step 4: Try to insert into DB (optional)
    # -------------------------------
    if db:
        try:
            # Upsert DimJokeType
            joke_type_obj = (await db.execute(select(DimJokeType).where(DimJokeType.name == joke_type_name))).scalar_one_or_none()
            if not joke_type_obj:
                joke_type_obj = DimJokeType(name=joke_type_name)
                db.add(joke_type_obj)
                await db.flush()

            # Upsert DimLanguage
            language_obj = (await db.execute(select(DimLanguage).where(DimLanguage.code == lang))).scalar_one_or_none()
            if not language_obj:
                language_obj = DimLanguage(code=lang, name=supported_langs.get(lang, lang))
                db.add(language_obj)
                await db.flush()

            # Insert FactJokes
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
        except Exception as e:
            logger.warning("DB insert failed, continuing anyway: %s", e)

    # -------------------------------
    # Step 5: Return joke
    # -------------------------------
    if joke_type_name == "single":
        return {"type": "single", "joke": joke_text}
    return {"type": "twopart", "setup": setup, "delivery": delivery}

@router.get("/debug-db-connection", response_class=JSONResponse)
async def debug_db_connection(db: AsyncSession = Depends(get_db)):
    """Test DB connectivity and log detailed errors."""
    try:
        await db.execute(select(1))
        logger.info("✅ DB connection successful")
        return {"status": "success", "message": "DB connection established"}
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        logger.error("❌ DB connection failed:\n%s", tb)
        return {"status": "error", "message": str(e), "traceback": tb}

# -------------------------------
# REGISTER ROUTER
# -------------------------------
app.include_router(router)
