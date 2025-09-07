# app/main.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
from pathlib import Path

app = FastAPI(title="Random Joke App")

# Define base directory
BASE_DIR = Path(__file__).resolve().parent

# Mount static folder for CSS and JS
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# Setup templates folder
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/", response_class=HTMLResponse)
async def read_main(request: Request):
    """
    Render the main page with the 'Get a Joke' button.
    """
    return templates.TemplateResponse(request, "index.html", {"request": request})


@app.get("/joke", response_class=JSONResponse)
async def get_joke():
    url = "https://v2.jokeapi.dev/joke/Any"
    async with httpx.AsyncClient() as client:
        res = await client.get(url)
        data = res.json()
        return data

