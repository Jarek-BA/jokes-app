from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
import os

# Base directory (absolute path to the app folder)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI()

# Mount static folder (absolute path)
static_dir = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Templates folder (absolute path)
templates_dir = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=templates_dir)

JOKE_API_URL = "https://v2.jokeapi.dev/joke/Any"

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/joke")
async def get_joke():
    async with httpx.AsyncClient() as client:
        response = await client.get(JOKE_API_URL)
        return response.json()
