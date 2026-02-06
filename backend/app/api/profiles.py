from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from app.schemas import BusinessProfileCreate, BusinessProfileUpdate, BusinessProfileResponse
from app.models import BusinessProfile

router = APIRouter()


@router.get("/", response_model=List[BusinessProfileResponse])
async def list_profiles(db: Session = Depends(get_db)):
    """List all business profiles"""
    # TODO: Filter by current user
    profiles = db.query(BusinessProfile).all()
    return profiles


@router.post("/", response_model=BusinessProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(profile_data: BusinessProfileCreate, db: Session = Depends(get_db)):
    """Create a new business profile"""
    # TODO: Get user_id from authenticated user
    # For now, using a placeholder
    new_profile = BusinessProfile(
        user_id="00000000-0000-0000-0000-000000000000",  # Placeholder
        **profile_data.model_dump()
    )
    
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    
    return new_profile


@router.get("/{profile_id}", response_model=BusinessProfileResponse)
async def get_profile(profile_id: UUID, db: Session = Depends(get_db)):
    """Get a specific business profile"""
    profile = db.query(BusinessProfile).filter(BusinessProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return profile


@router.put("/{profile_id}", response_model=BusinessProfileResponse)
async def update_profile(
    profile_id: UUID,
    profile_data: BusinessProfileUpdate,
    db: Session = Depends(get_db)
):
    """Update a business profile"""
    profile = db.query(BusinessProfile).filter(BusinessProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    
    # Update only provided fields
    for field, value in profile_data.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    
    db.commit()
    db.refresh(profile)
    
    return profile


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(profile_id: UUID, db: Session = Depends(get_db)):
    """Delete a business profile"""
    profile = db.query(BusinessProfile).filter(BusinessProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    
    db.delete(profile)
    db.commit()
    
    return None
