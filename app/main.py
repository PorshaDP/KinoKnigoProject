from fastapi import FastAPI, Depends, Form, HTTPException, status, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from sqlalchemy.orm import Session
from app.models import Base, User, SessionLocal, engine, create_user, get_user_by_email, get_user_by_name, hash_password, verify_password
from datetime import datetime, timedelta
import jwt

SECRET_KEY = "a2f6c1b3e8d9f7a2c3d4b5e6f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9g0"
ALGORITHM = "HS256"

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print(f"[DEBUG] Token created: {token}")
    return token

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"[DEBUG] Token verified: {payload}")
        return payload
    except jwt.ExpiredSignatureError:
        print("[DEBUG] Token expired")
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        print("[DEBUG] Invalid token")
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/", response_class=HTMLResponse)
async def auth_menu(request: Request):
    return templates.TemplateResponse("auth_menu.html", {"request": request})

@app.get("/main", response_class=HTMLResponse)
async def main_page(request: Request):
    return templates.TemplateResponse("main_page.html", {"request": request})

@app.get("/profile", response_class=HTMLResponse)
async def get_profile(request: Request, access_token: str = Cookie(None)):
    if not access_token:
        print("[DEBUG] Access token not found in cookies")
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_data = verify_token(access_token)
    db = next(get_db())
    user = get_user_by_email(db, user_data["sub"])
    if not user:
        print(f"[DEBUG] User not found for email in token: {user_data['sub']}")
        raise HTTPException(status_code=404, detail="User not found")

    return templates.TemplateResponse("profile.html", {"request": request, "user": {"name": user.name, "email": user.email}})

@app.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register", response_class=HTMLResponse)
async def register_user(request: Request, name: str = Form(...), email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    print(f"[DEBUG] Registering user: name={name}, email={email}")

    if get_user_by_email(db, email):
        print(f"[DEBUG] Email already in use: {email}")
        raise HTTPException(status_code=400, detail="Email уже используется")
    
    if get_user_by_name(db, name):
        print(f"[DEBUG] Username already taken: {name}")
        raise HTTPException(status_code=400, detail="Имя пользователя уже занято")
    
    hashed_password = hash_password(password)
    print(f"[DEBUG] Password hashed: {hashed_password}")

    create_user(db, name=name, email=email, password=hashed_password)
    print("[DEBUG] User created successfully")
    return RedirectResponse("/main", status_code=302)

@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login_user(
    request: Request, 
    email: str = Form(...), 
    password: str = Form(...), 
    db: Session = Depends(get_db)
):
    print(f"[DEBUG] Login attempt: email={email}")

    user = get_user_by_email(db, email)
    if not user:
        print(f"[DEBUG] User not found for email: {email}")
        raise HTTPException(status_code=400, detail="Неверные учетные данные")

    print(f"[DEBUG] User found: {user.name}, email={user.email}")

    if not verify_password(password, user.password):
        print(f"[DEBUG] Password mismatch for user: {email}")
        raise HTTPException(status_code=400, detail="Неверные учетные данные")

    print(f"[DEBUG] Password verified for user: {email}")

    access_token = create_access_token(data={"sub": user.email})
    print(f"[DEBUG] Access token created for user: {email}")

    response = RedirectResponse("/main", status_code=302)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    print(f"[DEBUG] Login successful for user: {email}, redirecting to /main")
    return response

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
