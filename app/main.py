from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx

app = FastAPI()

# Serve static files (CSS/JS)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates folder
templates = Jinja2Templates(directory="app/templates")

# JokeAPI URL
API_URL = "https://v2.jokeapi.dev/joke/Any"

@app.get("/joke")
async def get_joke():
    async with httpx.AsyncClient() as client:
        response = await client.get(API_URL)
        response.raise_for_status()
        data = response.json()

    if data["type"] == "single":
        joke = data["joke"]
    else:  # twopart
        joke = f'{data["setup"]} ... {data["delivery"]}'

    return {"joke": joke}

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
