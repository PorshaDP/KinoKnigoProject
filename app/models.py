from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, Session 
from sqlalchemy.ext.declarative import declarative_base
from passlib.context import CryptContext
from sqlalchemy import create_engine
import csv
import random
from app.parsing_horo import get_horoscope_and_top_category, get_movies_for_category, get_random_movies
import os
import logging

# Логирование для отладки
logging.basicConfig(level=logging.DEBUG)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    photo_path = Column(Text, nullable=True)

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Утилиты для работы с паролями
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# Утилиты для работы с пользователями
def create_user(db: Session, name: str, email: str, password: str):
    db_user = User(name=name, email=email, password=password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()
def get_user_by_name(db: Session, name: str):
    return db.query(User).filter(User.name == name).first()

def get_random_book():

    try:
        with open("app/learning/filtered_translated_books.csv", encoding="utf-8") as csvfile:
            reader = list(csv.DictReader(csvfile))
            book = random.choice(reader)
            return {
                #"title": book.get("title", "Не указано"),
                "authors": book.get("authors", "Не указано"),
                "published_year": book.get("published_year", "Не указано"),
                "categories": book.get("categories", "Не указано"),
                "thumbnail": book.get("thumbnail", ""),
                "description": book.get("description", "Описание отсутствует"),
                "average_rating": book.get("average_rating", "Нет рейтинга"),
                "num_pages": book.get("num_pages", "Нет данных о страницах"),
            }
    except FileNotFoundError:
        return {"error": "Файл с книгами не найден"}
    except Exception as e:
        return {"error": f"Произошла ошибка: {str(e)}"}



def get_random_movie():
    try:
        with open("app/learning/THUMBNAILS_translated_movies.csv", encoding="utf-8") as csvfile:
            reader = list(csv.DictReader(csvfile))
            movie = random.choice(reader)
            #movie_title = movie.get("Title", "Не указано")


            # Получаем alt_name для картинки
            alt_name = movie.get("alt_name")  # Используем alt_name, если он есть, иначе transliterated_title

            # Формируем путь к изображению относительно папки /static/
            image_folder = "app/static/movie_posters"
            image_filename = f"{alt_name}.jpg"  # или .png, если формат другой
            image_path = os.path.join(image_folder, image_filename)

            # Проверяем, существует ли файл изображения
            if not os.path.isfile(image_path):
                image_path = ""  # если изображения нет, возвращаем пустую строку
            else:
                # Путь для использования в HTML
                image_path = f"/static/movie_posters/{alt_name}.jpg"

            # Логирование для отладки
            logging.debug(f"Image path: {image_path}")

            return {
                "genre": movie.get("Genre", "Не указано"),
                "year": movie.get("Year", "Не указано"),
                "score": movie.get("Score", "Нет оценки"),
                "description": movie.get("Description", "Описание отсутствует"),
                "poster_url": image_path,  # Указываем путь к картинке
            }
    except FileNotFoundError:
        return {"error": "Файл с фильмами не найден"}
    except Exception as e:
        return {"error": f"Произошла ошибка: {str(e)}"}



def get_horoscope_and_movies(sign):
    horoscope, top_category_info = get_horoscope_and_top_category(sign)

    if horoscope and top_category_info:
        top_category, stars = top_category_info
        movies = get_movies_for_category(top_category)
        random_movies = get_random_movies(movies)

        return {
            "horoscope": horoscope,
            "top_category": top_category,
            "stars": stars,
            "movies": random_movies
        }

    return {"error": "Не удалось получить данные"}

# Функция для получения заголовков книг из CSV
def get_book_titles_from_csv(file_path):
    titles = []
    try:
        with open(file_path, mode='r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                title = row.get('title')
                if title:
                    titles.append(title)
    except FileNotFoundError:
        print(f"Ошибка: Файл {file_path} не найден.")
    except Exception as e:
        print(f"Ошибка при чтении файла CSV: {e}")
    return titles

# Функция для получения заголовков книг из CSV
def get_movies_titles_from_csv(file_path):
    titles = []
    try:
        with open(file_path, mode='r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                title = row.get('Title')
                if title:
                    titles.append(title)
    except FileNotFoundError:
        print(f"Ошибка: Файл {file_path} не найден.")
    except Exception as e:
        print(f"Ошибка при чтении файла CSV: {e}")
    return titles