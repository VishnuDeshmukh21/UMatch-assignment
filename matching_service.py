from typing import List, Set, Dict, Tuple
from sqlalchemy.orm import Session
import models
import math
from collections import Counter

def calculate_age_compatibility(user1_age: int, user2_age: int, min_age_pref: int = None, max_age_pref: int = None) -> float:
    """
    Calculate age compatibility score between two users
    
    Returns:
        float: Score between 0 and 1, where 1 is perfect compatibility
    """
    # Check if user2's age is within user1's preferences
    if min_age_pref and user2_age < min_age_pref:
        return 0.0
    if max_age_pref and user2_age > max_age_pref:
        return 0.0
    
    # Calculate normalized age difference (0 to 1 scale, where 1 is perfect match)
    age_diff = abs(user1_age - user2_age)
    # Maximum age difference for calculation (20 years difference = 0 score)
    max_age_diff = 20
    
    if age_diff >= max_age_diff:
        return 0.0
    
    return 1.0 - (age_diff / max_age_diff)

def calculate_interest_similarity(user1_interests: List[str], user2_interests: List[str]) -> Tuple[float, List[str]]:
    """
    Calculate interest similarity using Jaccard similarity
    
    Returns:
        Tuple[float, List[str]]: Similarity score (0-1) and list of common interests
    """
    user1_set = set(user1_interests)
    user2_set = set(user2_interests)
    
    if not user1_set or not user2_set:
        return 0.0, []
    
    common_interests = list(user1_set.intersection(user2_set))
    union_interests = user1_set.union(user2_set)
    
    # Jaccard similarity: size of intersection / size of union
    similarity = len(common_interests) / len(union_interests) if union_interests else 0.0
    
    return similarity, common_interests

def calculate_distance_compatibility(lat1: float, lon1: float, lat2: float, lon2: float, max_distance: int = 50) -> Tuple[float, float]:
    """
    Calculate geographical compatibility based on distance
    
    Returns:
        Tuple[float, float]: Score between 0 and 1, and the actual distance in km
    """
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return 0.0, None
    
    # Calculate distance using Haversine formula
    distance = models.User.calculate_distance(lat1, lon1, lat2, lon2)
    
    # If distance is greater than max_distance, compatibility is 0
    if distance > max_distance:
        return 0.0, distance
    
    # Normalize distance (0 to 1 scale, where 1 is perfect match)
    # Closer = higher score
    return 1.0 - (distance / max_distance), distance

def calculate_gender_preference_compatibility(user_gender: str, target_gender_pref: str) -> bool:
    """
    Check if users' gender preferences are compatible
    """
    if target_gender_pref is None:
        return True  # No preference specified
    
    # For simplicity, assuming gender_pref can be 'M', 'F', or 'Any'
    if target_gender_pref.lower() == 'any':
        return True
    
    return user_gender.upper() == target_gender_pref.upper()

def get_user_matches(db: Session, user_id: int, limit: int = 10) -> List[Dict]:
    """
    Find compatible matches for a given user
    
    Returns:
        List[Dict]: List of user dictionaries with compatibility scores
    """
    # Get the user
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return []
    
    # Get all users except the current user
    all_other_users = db.query(models.User).filter(models.User.id != user_id).all()
    
    # Get user interests as strings
    user_interests = [interest.name for interest in user.interests]
    
    # Calculate compatibility with each potential match
    matches = []
    for other_user in all_other_users:
        # Check gender preference compatibility
        # print(f"######## {other_user} ####")
        if not calculate_gender_preference_compatibility(other_user.gender, user.gender_pref):
            continue
        
        # Calculate age compatibility
        age_score = calculate_age_compatibility(
            user.age, 
            other_user.age, 
            user.min_age_pref, 
            user.max_age_pref
        )
        # print("age_score",age_score)
        
        # If age is incompatible, skip this user
        if age_score == 0:
            continue
        
        # Calculate interest similarity
        other_user_interests = [interest.name for interest in other_user.interests]
        interest_score, common_interests = calculate_interest_similarity(user_interests, other_user_interests)
        # print("interest_score",interest_score,common_interests)
        
        # Calculate distance compatibility
        if not user.distance_weight:
            # User does not care about distance, so set distance score to neutral (1.0)
            distance_score ,distance= 1.0,0
            print("Distance score is neutral (user doesn't care about distance)")
        else:
            # Calculate the distance score if user cares about distance
            distance_score, distance = calculate_distance_compatibility(
                user.latitude, 
                user.longitude, 
                other_user.latitude, 
                other_user.longitude,
                user.max_distance_pref
            )
            # print("Distance score:", distance_score)

            # If distance is incompatible, skip this user
            if distance_score == 0:
                continue

        
        # Calculate weighted compatibility score
        compatibility_score = (
            user.interest_weight * interest_score + 
            user.age_weight * age_score + 
            user.distance_weight * distance_score
        )
        # print("compatibility_score",compatibility_score)
        
        matches.append({
            "user_id": other_user.id,
            "name": other_user.name,
            "age": other_user.age,
            "gender": other_user.gender,
            "city": other_user.city,
            "distance": distance,
            "common_interests": common_interests,
            "compatibility_score": compatibility_score
        })
    
    # Sort matches by compatibility score (highest first)
    matches.sort(key=lambda x: x["compatibility_score"], reverse=True)
    
    # Return top N matches
    return matches[:limit]