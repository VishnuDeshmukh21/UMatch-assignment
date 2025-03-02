from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models, schemas
from pydantic import EmailStr

app = FastAPI()

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Validating email format using EmailStr in Pydantic
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Creating user
    db_user = models.User(name=user.name, age=user.age, gender=user.gender, email=user.email, city=user.city)
    
    # Creating interests and add them to the user
    interests = [models.Interest(name=interest.name) for interest in user.interests]
    db_user.interests = interests
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields of the user
    if user.name:
        db_user.name = user.name
    if user.age:
        db_user.age = user.age
    if user.gender:
        db_user.gender = user.gender
    if user.email:
        db_user.email = user.email
    if user.city:
        db_user.city = user.city
    
    # Update interests (with interests if any)
    if user.interests:
        for interest in user.interests:
            existing_interest = db.query(models.Interest).filter(models.Interest.name == interest.name, models.Interest.user_id == user_id).first()
            if not existing_interest:
                # Create new interest if it doesn't exist
                new_interest = models.Interest(name=interest.name, user_id=user_id)
                db.add(new_interest)
            else:
                existing_interest.name = interest.name
            
    db.commit()
    db.refresh(db_user)
    return db_user


@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Delete user and their interests
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

@app.get("/users/{user_id}/matches", response_model=list[schemas.User])
def find_matches(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    potential_matches = db.query(models.User).filter(
        models.User.id != user.id,
        models.User.city == user.city,
        models.User.gender != user.gender,
        models.User.interests.any(models.Interest.name.in_([interest.name for interest in user.interests]))
    ).all()
    
    return potential_matches