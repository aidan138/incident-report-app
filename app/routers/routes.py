from fastapi import APIRouter, Depends, HTTPException
from ..crud import crud
from ..models import models
from ..schemas import schemas
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from .. import db

router = APIRouter()

@router.post('/create-lifeguard/', response_model=schemas.Lifeguard)
async def create_lifeguard(lg: schemas.LifeguardCreate, db: AsyncSession = Depends(db.get_db)):
    try:
        existing = await crud.get_lifeguard_by_phone(db, lg.phone)
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail=f"Failed to get lifeguard information from phone number {lg.phone}")
    
    if existing:
            raise HTTPException(status_code=400, detail="Lifeguard exists")
    
    try:
        new_lg = crud.create_lifeguard(db, lg)
        return new_lg
    except SQLAlchemyError:
         HTTPException(status_code=500, detail="Internal server error inserting lifeguard into the database")