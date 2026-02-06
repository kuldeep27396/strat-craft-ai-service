from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from app.schemas import QuestionnaireCreate, QuestionnaireUpdate, QuestionnaireResponse
from app.models import Questionnaire

router = APIRouter()


@router.get("/", response_model=List[QuestionnaireResponse])
async def list_questionnaires(db: Session = Depends(get_db)):
    """List all questionnaires"""
    questionnaires = db.query(Questionnaire).all()
    return questionnaires


@router.post("/", response_model=QuestionnaireResponse, status_code=status.HTTP_201_CREATED)
async def create_questionnaire(questionnaire_data: QuestionnaireCreate, db: Session = Depends(get_db)):
    """Create a new questionnaire"""
    new_questionnaire = Questionnaire(**questionnaire_data.model_dump())
    
    db.add(new_questionnaire)
    db.commit()
    db.refresh(new_questionnaire)
    
    return new_questionnaire


@router.get("/{questionnaire_id}", response_model=QuestionnaireResponse)
async def get_questionnaire(questionnaire_id: UUID, db: Session = Depends(get_db)):
    """Get a specific questionnaire"""
    questionnaire = db.query(Questionnaire).filter(Questionnaire.id == questionnaire_id).first()
    if not questionnaire:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Questionnaire not found")
    return questionnaire


@router.put("/{questionnaire_id}", response_model=QuestionnaireResponse)
async def update_questionnaire(
    questionnaire_id: UUID,
    questionnaire_data: QuestionnaireUpdate,
    db: Session = Depends(get_db)
):
    """Update a questionnaire"""
    questionnaire = db.query(Questionnaire).filter(Questionnaire.id == questionnaire_id).first()
    if not questionnaire:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Questionnaire not found")
    
    for field, value in questionnaire_data.model_dump(exclude_unset=True).items():
        setattr(questionnaire, field, value)
    
    db.commit()
    db.refresh(questionnaire)
    
    return questionnaire


@router.delete("/{questionnaire_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_questionnaire(questionnaire_id: UUID, db: Session = Depends(get_db)):
    """Delete a questionnaire"""
    questionnaire = db.query(Questionnaire).filter(Questionnaire.id == questionnaire_id).first()
    if not questionnaire:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Questionnaire not found")
    
    db.delete(questionnaire)
    db.commit()
    
    return None
