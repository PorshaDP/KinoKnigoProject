from fastapi import FastAPI, Depends, Form, HTTPException, status, Cookie, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from sqlalchemy.orm import Session
from app.models import Base, User, SessionLocal, engine, create_user, get_user_by_email, get_user_by_name, hash_password, verify_password
from datetime import datetime, timedelta
import jwt, os

from app.learning import new_model, translated_model_for_movies, translated_model_for_books

from pydantic import BaseModel
from app.models import get_random_book, get_random_movie

from app.models import get_horoscope_and_movies  

# Настройки приложения
SECRET_KEY = "a2f6c1b3e8d9f7a2c3d4b5e6f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9g0"
ALGORITHM = "HS256"

app = FastAPI()

# Настройка путей к шаблонам и статическим файлам
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Директория для загрузки файлов
UPLOAD_DIR = "app/static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Инициализация базы данных
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Функция для создания JWT токена
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

# Функция для проверки токена
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Главная страница
@app.get("/", response_class=HTMLResponse)
async def auth_menu(request: Request):
    return templates.TemplateResponse("auth_menu.html", {"request": request})

# Главная страница приложения
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
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_data = verify_token(access_token)
    user = get_user_by_email(db, user_data["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")


    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    

    if not os.path.exists(file_path):
        raise HTTPException(status_code=500, detail="Ошибка сохранения файла")

    user.photo_path = f"/static/uploads/{file.filename}"
    db.add(user)
    db.commit()

    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": {"name": user.name, "email": user.email, "photo_path": user.photo_path}
    })

@app.post("/delete_photo", response_class=HTMLResponse)
async def delete_photo(request: Request, access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_data = verify_token(access_token)
    db = next(get_db())
    user = get_user_by_email(db, user_data["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Удаление файла, если он существует
    if user.photo_path and os.path.exists(user.photo_path[1:]):
        os.remove(user.photo_path[1:])

    # Сброс значения photo_path в базе данных
    user.photo_path = None
    db.add(user)
    db.commit()

    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": {"name": user.name, "email": user.email, "photo_path": None}
    })
# Регистрация
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

# Авторизация
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

# Модель запроса для фильмов
class MovieRequest(BaseModel):
    title: str
    num_recommendations: int = 5


# Эндпоинт для обучения модели
@app.post("/train_model_movies")
async def train_model():
    result = translated_model_for_movies.train_model()
    if 'error' in result:
        raise HTTPException(status_code=400, detail=result['error'])
    return result

# Эндпоинт для получения рекомендаций
@app.post("/recommend_movies")
async def recommend_movies(request: MovieRequest):
    recommendations = translated_model_for_movies.recommend_movies(request.title, request.num_recommendations)
    if "error" in recommendations:
        raise HTTPException(status_code=404, detail=recommendations["error"])
    return recommendations


class BookRequest(BaseModel):
    title: str  # Название книги
    num_recommendations: int = 10  # Количество рекомендаций (по умолчанию 10)

# Эндпоинт для обучения модели
@app.post("/train_model_books")
async def train_model():
    result = translated_model_for_books.train_model()
    if 'error' in result:
        raise HTTPException(status_code=400, detail=result['error'])
    return result

# Эндпоинт для получения рекомендаций
@app.post("/recommend_books")
async def recommend_books(request: BookRequest):
    recommendations = translated_model_for_books.recommend_books(request.title, request.num_recommendations)
    if "error" in recommendations:
        raise HTTPException(status_code=404, detail=recommendations["error"])
    return recommendations

@app.get("/movies", response_class=HTMLResponse)
async def get_movie(request: Request):
    return templates.TemplateResponse("movie.html", {"request": request})

# Модель запроса для книг
class BookRequest(BaseModel):
    title: str
    num_recommendations: int = 10

# Рекомендации книг
@app.post("/recommend_books")
async def recommend_books(request: BookRequest):
    recommendations = new_model_for_books.recommend_books(request.title, request.num_recommendations)
    if "error" in recommendations:
        raise HTTPException(status_code=404, detail=recommendations["error"])
    return recommendations


# Страница книг
@app.get("/books", response_class=HTMLResponse)
async def get_books_page(request: Request):
    return templates.TemplateResponse("books.html", {"request": request})



@app.get("/random", response_class=HTMLResponse)
async def randomizer(request: Request):

    random_book = get_random_book()
    random_movie = get_random_movie()

    return templates.TemplateResponse("random.html", {
        "request": request,
        "book": random_book,
        "movie": random_movie,
    })

# Обработчик GET запроса для отображения формы
@app.get("/get_horoscope")
async def get_horoscope_form(request: Request):
    return templates.TemplateResponse("horoscope.html", {"request": request})

@app.post("/get_horoscope")
async def get_horoscope(request: Request, sign: str = Form(...)):
    result = get_horoscope_and_movies(sign)

    if "error" in result:
        return templates.TemplateResponse("error.html", {"request": request, "error": result["error"]})

    horoscope = result["horoscope"]
    top_category = result["top_category"]
    stars = result["stars"]
    random_movies = result["movies"]

    # Добавляем к каждому фильму дополнительные данные, такие как картинка, описание, год и рейтинг
    # Пример:
    for movie in random_movies:
        movie["poster_url"] = movie.get("poster_url", "default_thumbnail.jpg")  # Если нет картинки, ставим дефолт
        movie["year"] = movie.get("year", "Не указан")
        movie["rating"] = movie.get("rating", "Не указан")
        movie["description"] = movie.get("description", "Описание отсутствует")

    return templates.TemplateResponse("result.html", {
        "request": request, 
        "horoscope": horoscope, 
        "top_category": top_category, 
        "stars": stars, 
        "random_movies": random_movies,
        "sign": sign  
    })

def zodiac_translation(sign: str):
    translations = {
        'aries': 'Овнов',
        'taurus': 'Тельцов',
        'gemini': 'Близнецов',
        'cancer': 'Раков',
        'leo': 'Львов',
        'virgo': 'Дев',
        'libra': 'Весов',
        'scorpio': 'Скорпионов',
        'sagittarius': 'Стрельцов',
        'capricorn': 'Козерогов',
        'aquarius': 'Водолеев',
        'pisces': 'Рыб',
    }
    return translations.get(sign.lower(), sign.capitalize())

templates.env.filters["zodiac_translation"] = zodiac_translation