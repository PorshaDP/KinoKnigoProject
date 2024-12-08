from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, Session 
from sqlalchemy.ext.declarative import declarative_base
from passlib.context import CryptContext
from sqlalchemy import create_engine
import csv
import random

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    photo_path = Column(Text, nullable=True)  

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

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
        with open("app/learning/filtered_books.csv", encoding="utf-8") as csvfile:
            reader = list(csv.DictReader(csvfile))
            book = random.choice(reader)
            return {
                "title": book.get("Title", "Не указано"),
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
        with open("app/learning/filtered_movies.csv", encoding="utf-8") as csvfile:
            reader = list(csv.DictReader(csvfile))
            movie = random.choice(reader)
            return {
                "title": movie.get("title", "Не указано"),
                "genre": movie.get("Genre", "Не указано"),
                "year": movie.get("Year", "Не указано"),
                "score": movie.get("Score", "Нет оценки"),
                "description": movie.get("Description", "Описание отсутствует"),
            }
    except FileNotFoundError:
        return {"error": "Файл с фильмами не найден"}
    except Exception as e:
        return {"error": f"Произошла ошибка: {str(e)}"}