from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.database import get_db
from app.schemas import StrategyGenerate, StrategyResponse, StrategyUpdate
from app.models import Strategy, Questionnaire

router = APIRouter()


@router.post("/generate", response_model=StrategyResponse, status_code=status.HTTP_201_CREATED)
async def generate_strategy(strategy_request: StrategyGenerate, db: Session = Depends(get_db)):
    """Generate a new marketing strategy from questionnaire"""
    # Verify questionnaire exists
    questionnaire = db.query(Questionnaire).filter(
        Questionnaire.id == strategy_request.questionnaire_id
    ).first()
    if not questionnaire:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Questionnaire not found")
    
    # Create strategy record with 'generating' status
    new_strategy = Strategy(
        questionnaire_id=strategy_request.questionnaire_id,
        status="generating",
        strategy_content={}
    )
    
    db.add(new_strategy)
    db.commit()
    db.refresh(new_strategy)
    
    # SIMULATION: Generate Mock Strategy immediately for MVP Demo
    # In production, this would be a background Celery task
    mock_content = {
        "title": f"Growth Strategy for {questionnaire.client_name or 'Client'}",
        "sections": [
            {
                "heading": "Executive Summary",
                "content": f"Based on the analysis of {questionnaire.client_name or 'your business'}, we have identified a significant opportunity to capture market share through a targeted SEO and Content approach. The primary focus should be on solving '{questionnaire.problem_statement or 'customer pain points'}' by highlighting your unique value proposition.",
                "tactics": [
                    "Launch targeted content hub around core topics",
                    "Optimize conversion paths for high-intent visitors",
                    "Implement automated lead nurturing sequences"
                ],
                "kpis": [
                    "Increase Organic Traffic by 40% in Q1",
                    "Generate 50+ MQLs monthly",
                    "Achieve Top 3 ranking for primary keywords"
                ]
            },
            {
                "heading": "SEO & Organic Search Strategy",
                "content": "Your technical foundation is solid, but content depth is lacking compared to competitors. We recommend a 'Hub and Spoke' model.",
                "tactics": [
                    "Technical Audit & Core Web Vitals optimizaton",
                    "Create 10 'Skyscraper' articles for high-volume keywords",
                    "Backlink acquisition campaign targeting industry publications"
                ],
                "kpis": [
                    "Domain Authority (DA) > 40",
                    "Keyword Visibility Score > 15%"
                ]
            },
            {
                "heading": "Content Marketing Roadmap",
                "content": f"To address the needs of your ICP ({questionnaire.target_icp or 'Target Audience'}), content must shift from product-centric to problem-centric.",
                "tactics": [
                    "Weekly case study publication",
                    "LinkedIn thought leadership series for founders",
                    "Gated whitepaper for lead capture"
                ],
                "kpis": [
                    "Social Engagement Rate > 3%",
                    "Whitepaper downloads: 100/month"
                ]
            }
        ],
        "pricing": {
            "monthly_cost": 4500,
            "team": ["SEO Specialist", "Content Writer", "Account Manager"]
        }
    }
    
    new_strategy.strategy_content = mock_content
    new_strategy.status = "completed"
    
    db.add(new_strategy)
    db.commit()
    db.refresh(new_strategy)
    
    return new_strategy


@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(strategy_id: UUID, db: Session = Depends(get_db)):
    """Get a specific strategy"""
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Strategy not found")
    return strategy


@router.get("/{strategy_id}/status")
async def get_strategy_status(strategy_id: UUID, db: Session = Depends(get_db)):
    """Get generation status of a strategy"""
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Strategy not found")
    
    return {
        "id": strategy.id,
        "status": strategy.status,
        "progress": 100 if strategy.status == "completed" else 50  # Placeholder
    }


@router.put("/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(
    strategy_id: UUID,
    strategy_data: StrategyUpdate,
    db: Session = Depends(get_db)
):
    """Update/edit a strategy"""
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Strategy not found")
    
    strategy.strategy_content = strategy_data.strategy_content
    strategy.version += 1
    
    db.commit()
    db.refresh(strategy)
    
    return strategy


@router.post("/{strategy_id}/export")
async def export_strategy(strategy_id: UUID, db: Session = Depends(get_db)):
    """Export strategy to PDF"""
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Strategy not found")
    if strategy.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Strategy is not completed yet"
        )
    
    # TODO: Implement PDF export
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="PDF export coming soon")
