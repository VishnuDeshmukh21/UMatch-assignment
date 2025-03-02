from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Set

class InterestBase(BaseModel):
    name: str

class Interest(InterestBase):
    id: int
    
    class Config:
        orm_mode = True

class UserPreferences(BaseModel):
    min_age_pref: Optional[int] = None
    max_age_pref: Optional[int] = None
    gender_pref: Optional[str] = None
    max_distance_pref: Optional[int] = 50
    
    # Weights for the compatibility score calculation
    interest_weight: Optional[float] = 0.4
    age_weight: Optional[float] = 0.3
    distance_weight: Optional[float] = 0.3

class UserLocation(BaseModel):
    latitude: float
    longitude: float

class UserBase(BaseModel):
    name: str
    age: int
    gender: str
    email: EmailStr
    city: str

class UserCreate(UserBase):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    interests: List[str] = []
    min_age_pref: Optional[int] = None
    max_age_pref: Optional[int] = None
    gender_pref: Optional[str] = None
    max_distance_pref: Optional[int] = 50
    interest_weight: Optional[float] = 0.4
    age_weight: Optional[float] = 0.3
    distance_weight: Optional[float] = 0.3

class UserUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    interests: Optional[List[str]] = None
    min_age_pref: Optional[int] = None
    max_age_pref: Optional[int] = None
    gender_pref: Optional[str] = None
    max_distance_pref: Optional[int] = None
    interest_weight: Optional[float] = None
    age_weight: Optional[float] = None
    distance_weight: Optional[float] = None

class User(UserBase):
    id: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    interests: List[Interest] = []
    min_age_pref: Optional[int] = None
    max_age_pref: Optional[int] = None
    gender_pref: Optional[str] = None
    max_distance_pref: Optional[int] = 50
    interest_weight: float = 0.4
    age_weight: float = 0.3
    distance_weight: float = 0.3
    
    class Config:
        orm_mode = True

class MatchScore(BaseModel):
    user_id: int
    name: str
    age: int
    gender: str
    city: str
    distance: Optional[float] = None
    common_interests: List[str] = []
    compatibility_score: float
    
    class Config:
        orm_mode = True