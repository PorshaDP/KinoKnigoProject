from fastapi import FastAPI, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
#from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from app.models import User

app = FastAPI()


templates = Jinja2Templates(directory="app/templates")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

#oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/", response_class=HTMLResponse)
async def auth_menu(request: Request):
    return templates.TemplateResponse("auth_menu.html", {"request": request})


@app.get("/main", response_class=HTMLResponse)
async def main_page(request: Request):
    return templates.TemplateResponse("main_page.html", {"request": request})


@app.get("/profile", response_class=HTMLResponse)#, token: str = Depends(oauth2_scheme)
async def get_profile(request: Request):
    user = {"name": "Jane Doe", "email": "AdepteShchyao@yandex.ru", "avatar": "avatar.jpg"}
    return templates.TemplateResponse("profile.html", {"request": request, "user": user})


@app.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register", response_class=HTMLResponse)
async def register_user(request: Request, name: str = Form(...), email: str = Form(...)):
    user = User(name=name, email=email)
    return RedirectResponse("/main", status_code=302)


@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login_user(request: Request, email: str = Form(...), password: str = Form(...)):
    user = {"name": "Jane Doe", "email": email}
    return RedirectResponse("/main", status_code=302)


@app.get("/books", response_class=HTMLResponse)
async def get_books(request: Request):
    books = [{"id": 1, "title": "Book 1"}, {"id": 2, "title": "Book 2"}]
    return templates.TemplateResponse("books.html", {"request": request, "books": books})


@app.get("/movies", response_class=HTMLResponse)
async def get_movies(request: Request):
    movies = [{"id": 1, "title": "Movie 1"}, {"id": 2, "title": "Movie 2"}]
    return templates.TemplateResponse("movies.html", {"request": request, "movies": movies})


@app.get("/random", response_class=HTMLResponse)
async def random_recommendation(request: Request):
    random_book = {"id": 1, "title": "Random Book"}
    random_movie = {"id": 1, "title": "Random Movie"}
    return templates.TemplateResponse("random.html", {"request": request, "book": random_book, "movie": random_movie})
"""
"""