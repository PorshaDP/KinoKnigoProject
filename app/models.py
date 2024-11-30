from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker, Session 
from sqlalchemy.ext.declarative import declarative_base
from passlib.context import CryptContext
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db" 
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    hashed = pwd_context.hash(password)
    print(f"[DEBUG] Password hashed: {hashed}")
    return hashed

def verify_password(plain_password: str, hashed_password: str):
    is_valid = pwd_context.verify(plain_password, hashed_password)
    print(f"[DEBUG] Password verification: plain={plain_password}, hashed={hashed_password}, valid={is_valid}")
    return is_valid

def create_user(db: Session, name: str, email: str, password: str):
    print(f"[DEBUG] Creating user: name={name}, email={email}")
    db_user = User(name=name, email=email, password=password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    print(f"[DEBUG] User created: id={db_user.id}, name={db_user.name}, email={db_user.email}")
    return db_user

def get_user_by_email(db: Session, email: str):
    print(f"[DEBUG] Searching user by email: {email}")
    user = db.query(User).filter(User.email == email).first()
    if user:
        print(f"[DEBUG] User found: id={user.id}, name={user.name}, email={user.email}")
    else:
        print(f"[DEBUG] No user found with email: {email}")
    return user

def get_user_by_name(db: Session, name: str):
    print(f"[DEBUG] Searching user by name: {name}")
    user = db.query(User).filter(User.name == name).first()
    if user:
        print(f"[DEBUG] User found: id={user.id}, name={user.name}, email={user.email}")
    else:
        print(f"[DEBUG] No user found with name: {name}")
    return user
