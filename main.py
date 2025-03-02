from fastapi import FastAPI, HTTPException, Depends, Query,status
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models, schemas
from pydantic import EmailStr, ValidationError
from typing import List, Optional
from matching_service import get_user_matches
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

app = FastAPI()

# Create tables in the database
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    # Extract the errors
    error_details = []
    
    for err in exc.errors():
        if err['loc'][-1] == 'email':
            error_details.append("Invalid email format")
        else:
            error_details.append(f"Invalid input in field: {err['loc'][-1]}")
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Validation failed", "errors": error_details}
    )

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        # Check if email already exists
        if db.query(models.User).filter(models.User.email == user.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")

        # Create user
        db_user = models.User(
            name=user.name,
            age=user.age,
            gender=user.gender,
            email=user.email,
            city=user.city,
            latitude=user.latitude,
            longitude=user.longitude,
            min_age_pref=user.min_age_pref,
            max_age_pref=user.max_age_pref,
            gender_pref=user.gender_pref,
            max_distance_pref=user.max_distance_pref,
            interest_weight=user.interest_weight,
            age_weight=user.age_weight,
            distance_weight=user.distance_weight
        )
        
        # Add user to the database to get user_id
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # Add interests for the user
        for interest_name in user.interests:
            interest = db.query(models.Interest).filter(models.Interest.name == interest_name).first()
            if not interest:
                interest = models.Interest(name=interest_name)
                db.add(interest)
                db.commit()
                db.refresh(interest)
            db_user.interests.append(interest)

        db.commit()
        db.refresh(db_user)

        return db_user
    
    except Exception as e:
        # Catch all unexpected errors
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": f"An unexpected error occurred: {str(e)}"}
        )

@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
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
    
    # Update basic user fields if provided
    for field, value in user.dict(exclude_unset=True).items():
        if field != "interests" and value is not None:
            setattr(db_user, field, value)
    
    # Update interests if provided
    if user.interests:
        # Clear existing interests
        db_user.interests = []
        
        # Add new interests
        for interest_name in user.interests:
            # Check if interest already exists
            interest = db.query(models.Interest).filter(models.Interest.name == interest_name).first()
            if not interest:
                # Create new interest
                interest = models.Interest(name=interest_name)
                db.add(interest)
                db.commit()
                db.refresh(interest)
            
            # Add interest to user
            db_user.interests.append(interest)
    
    db.commit()
    db.refresh(db_user)
    return db_user

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Delete user (interests will be automatically handled by SQLAlchemy through the association table)
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

@app.post("/users/{user_id}/location", response_model=schemas.User)
def update_user_location(
    user_id: int, 
    location: schemas.UserLocation, 
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.latitude = location.latitude
    user.longitude = location.longitude
    
    db.commit()
    db.refresh(user)
    return user

@app.post("/users/{user_id}/preferences", response_model=schemas.User)
def update_user_preferences(
    user_id: int, 
    preferences: schemas.UserPreferences, 
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update preferences
    for field, value in preferences.dict(exclude_unset=True).items():
        if value is not None:
            setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user

@app.get("/users/{user_id}/matches", response_model=List[schemas.MatchScore])
def get_matches(
    user_id: int, 
    limit: int = Query(10, ge=1, le=100), 
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get matches using the matching service
    matches = get_user_matches(db, user_id, limit)
    return matches

@app.get("/interests/", response_model=List[schemas.Interest])
def read_interests(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    interests = db.query(models.Interest).offset(skip).limit(limit).all()
    return interests