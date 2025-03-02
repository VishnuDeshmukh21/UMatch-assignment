from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship
from database import Base
import math

# Association table for many-to-many relationship between users and interests
user_interest = Table(
    "user_interest",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("interest_id", Integer, ForeignKey("interests.id"))
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    gender = Column(String)
    email = Column(String, unique=True, index=True)
    city = Column(String)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Preferences
    min_age_pref = Column(Integer, nullable=True)
    max_age_pref = Column(Integer, nullable=True)
    gender_pref = Column(String, nullable=True)
    max_distance_pref = Column(Integer, nullable=True, default=50)  # in kilometers
    
    # Interest weights
    interest_weight = Column(Float, default=0.4)
    age_weight = Column(Float, default=0.3)
    distance_weight = Column(Float, default=0.3)
    
    # Relationships
    interests = relationship("Interest", secondary=user_interest, back_populates="users")
    
    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, age={self.age}, gender={self.gender}, email={self.email}, city={self.city})>"
    
    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        """Calculate distance between two points using Haversine formula"""
        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        r = 6371  # Radius of earth in kilometers
        return c * r

class Interest(Base):
    __tablename__ = "interests"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    
    # Relationships
    users = relationship("User", secondary=user_interest, back_populates="interests")
    
    def __repr__(self):
        return f"<Interest(id={self.id}, name={self.name})>"