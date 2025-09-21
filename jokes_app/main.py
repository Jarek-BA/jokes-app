# jokes_app/main.py

# Import the FastAPI framework, which is used to build web applications and APIs.
# Think of FastAPI as the "engine" that powers this app.
from fastapi import FastAPI, Request, Query

# Import two types of responses:
# - HTMLResponse: sends back a webpage (HTML).
# - JSONResponse: sends back data in a structured format (JSON), often used by APIs.
from fastapi.responses import HTMLResponse, JSONResponse

# Import StaticFiles: allows the app to serve CSS, JavaScript, and images
# so that the web page looks nice and works properly.
from fastapi.staticfiles import StaticFiles

# Import Jinja2Templates: a system that lets us insert dynamic content
# (like jokes) into HTML pages before sending them to the user.
from fastapi.templating import Jinja2Templates

# Import httpx: a library for making requests to other websites or APIs.
# We use it here to connect to the "Joke API" and fetch jokes.
import httpx

# Import Path from Python’s built-in pathlib library.
# Path helps us work with file and folder locations on the computer in a clean way.
from pathlib import Path


# -------------------------------
# CREATE THE APP
# -------------------------------

# Create an instance of the FastAPI app.
# This is like turning on the engine of our joke application.
# The "title" is just a label that shows up in documentation or debugging tools.
app = FastAPI(title="Random Joke App")


# -------------------------------
# DEFINE IMPORTANT FOLDERS
# -------------------------------

# BASE_DIR is the folder where this file (main.py) is located.
# "resolve()" finds the full absolute path.
# "parent" goes one level up (the folder that contains main.py).
BASE_DIR = Path(__file__).resolve().parent

# Mount (attach) the "static" folder so that the app can serve files like CSS (for styling)
# or JavaScript (for interactivity). These files are located in jokes_app/static.
# When a user’s browser requests "/static/...something...", FastAPI will look inside that folder.
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# Setup the "templates" folder.
# This is where we put HTML files that can display dynamic content (like jokes).
# We will use Jinja2 templates, which let us insert data into HTML pages.
templates = Jinja2Templates(directory=BASE_DIR / "templates")


# -------------------------------
# DEFINE ROUTES (PAGES / ENDPOINTS)
# -------------------------------

# ROUTE 1: The homepage ("/")
@app.get("/", response_class=HTMLResponse)  # This means: when someone visits "/", return an HTML page.
async def read_main(request: Request):
    """
    Show the homepage with a button labeled 'Get a Joke'.
    """
    # Use the "index.html" template from the templates folder.
    # Pass in the "request" object, which is required by FastAPI/Jinja2
    # to render the page correctly.
    return templates.TemplateResponse(request, "index.html", {"request": request})


# ROUTE 2: The joke endpoint ("/joke")
@app.get("/joke", response_class=JSONResponse)
async def get_joke(lang: str = "en", blacklist: str = ""):
    # ✅ Validate language
    if lang not in ["cs", "de", "en", "es", "fr"]:
        lang = "en"  # fallback to English

    # ✅ Build API URL with language
    url = f"https://v2.jokeapi.dev/joke/Any?lang={lang}"

    # ✅ Handle blacklist flags if provided
    if blacklist:
        url += f"&blacklistFlags={blacklist}"

    # ✅ Log the request details
    print(f"[DEBUG] Fetching joke with lang='{lang}', blacklist='{blacklist}'")

    async with httpx.AsyncClient() as client:
        res = await client.get(url)
        data = res.json()

    # ✅ Log the joke type (useful for debugging)
    joke_type = data.get("type", "unknown")
    print(f"[DEBUG] Joke fetched (type='{joke_type}')")

    return data
