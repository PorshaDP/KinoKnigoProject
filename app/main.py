from fastapi import FastAPI, Depends, Form, HTTPException, status, Cookie, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from sqlalchemy.orm import Session
from app.models import Base, User, SessionLocal, engine, create_user, get_user_by_email, get_user_by_name, hash_password, verify_password
from datetime import datetime, timedelta
import jwt
import os
from app.learning import new_model, new_model_for_books
from pydantic import BaseModel


SECRET_KEY = "a2f6c1b3e8d9f7a2c3d4b5e6f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9g0"
ALGORITHM = "HS256"

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

UPLOAD_DIR = "app/static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

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
    return token

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
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
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_data = verify_token(access_token)
    db = next(get_db())
    user = get_user_by_email(db, user_data["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": {"name": user.name, "email": user.email, "photo_path": user.photo_path}
    })

@app.post("/upload_photo", response_class=HTMLResponse)
async def upload_photo(
    request: Request,
    access_token: str = Cookie(None),
    file: UploadFile = File(...)
):
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_data = verify_token(access_token)
    db = next(get_db())
    user = get_user_by_email(db, user_data["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Сохранение файла
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # Обновление записи пользователя
    user.photo_path = f"/static/uploads/{file.filename}"
    db.add(user)
    db.commit()
    
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": {"name": user.name, "email": user.email, "photo_path": user.photo_path}
    })

@app.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register", response_class=HTMLResponse)
async def register_user(request: Request, name: str = Form(...), email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if get_user_by_email(db, email):
        raise HTTPException(status_code=400, detail="Email уже используется")
    
    if get_user_by_name(db, name):
        raise HTTPException(status_code=400, detail="Имя пользователя уже занято")
    
    hashed_password = hash_password(password)
    create_user(db, name=name, email=email, password=hashed_password)
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
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=400, detail="Неверные учетные данные")

    access_token = create_access_token(data={"sub": user.email})
    response = RedirectResponse("/main", status_code=302)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response

# Модель запроса для получения рекомендаций
class MovieRequest(BaseModel):
    title: str
    num_recommendations: int = 5

# Эндпоинт для обучения модели
@app.post("/train_model")
async def train_model():
    result = new_model.train_model()
    if 'error' in result:
        raise HTTPException(status_code=400, detail=result['error'])
    return result

# Эндпоинт для получения рекомендаций
@app.post("/recommend_movies")
async def recommend_movies(request: MovieRequest):
    recommendations = new_model.recommend_movies(request.title, request.num_recommendations)
    if "error" in recommendations:
        raise HTTPException(status_code=404, detail=recommendations["error"])
    return recommendations

class BookRequest(BaseModel):
    title: str  # Название книги
    num_recommendations: int = 10  # Количество рекомендаций (по умолчанию 10)

# Эндпоинт для обучения модели
@app.post("/train_model_books")
async def train_model():
    result = new_model_for_books.train_model()
    if 'error' in result:
        raise HTTPException(status_code=400, detail=result['error'])
    return result

# Эндпоинт для получения рекомендаций
@app.post("/recommend_books")
async def recommend_books(request: BookRequest):
    recommendations = new_model_for_books.recommend_books(request.title, request.num_recommendations)
    if "error" in recommendations:
        raise HTTPException(status_code=404, detail=recommendations["error"])
    return recommendations