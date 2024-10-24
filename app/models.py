from pydantic import BaseModel


class User(BaseModel):
    name: str
    email: str
    avatar: str = "default_avatar.png"
    liked_books: list = []
    liked_movies: list = []


class Book(BaseModel):
    id: int
    title: str
    description: str


class Movie(BaseModel):
    id: int
    title: str
    description: str
