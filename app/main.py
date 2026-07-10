from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from . import auth, models, schemas
from .database import Base, SessionLocal, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Todo App")


@app.post("/auth/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username == user_in.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    user = models.User(
        username=user_in.username,
        hashed_password=auth.hash_password(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth.create_access_token({"sub": user.username})
    return schemas.Token(access_token=token)


def _get_owned_todo(db: Session, todo_id: int, user: models.User) -> models.Todo:
    todo = (
        db.query(models.Todo)
        .filter(models.Todo.id == todo_id, models.Todo.owner_id == user.id)
        .first()
    )
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@app.post("/todos", response_model=schemas.TodoOut, status_code=status.HTTP_201_CREATED)
def create_todo(
    todo_in: schemas.TodoCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    todo = models.Todo(**todo_in.model_dump(), owner_id=current_user.id)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


@app.get("/todos", response_model=List[schemas.TodoOut])
def list_todos(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return db.query(models.Todo).filter(models.Todo.owner_id == current_user.id).all()


@app.get("/todos/{todo_id}", response_model=schemas.TodoOut)
def get_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return _get_owned_todo(db, todo_id, current_user)


@app.put("/todos/{todo_id}", response_model=schemas.TodoOut)
def update_todo(
    todo_id: int,
    todo_in: schemas.TodoUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    todo = _get_owned_todo(db, todo_id, current_user)
    for field, value in todo_in.model_dump(exclude_unset=True).items():
        setattr(todo, field, value)
    db.commit()
    db.refresh(todo)
    return todo


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    todo = _get_owned_todo(db, todo_id, current_user)
    db.delete(todo)
    db.commit()
    return None


@app.get("/health")
def health():
    return {"status": "ok"}
