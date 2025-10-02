from fastapi import APIRouter, Depends, HTTPException
from app.crud import crud
from app.schemas import portal_schemas
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.db import get_db

router = APIRouter()

@router.get('/get-lifeguard-by-phone-{phone_num}', response_model=portal_schemas.Lifeguard)
async def get_lifeguard_by_phone(phone: str, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.get_lifeguard_by_phone(db, phone)
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail=f"Failed to get lifeguard information from phone number {phone}")
    

@router.post('/create-lifeguard/', response_model=portal_schemas.Lifeguard)
async def create_lifeguard(lg: portal_schemas.LifeguardPayload, db: AsyncSession = Depends(get_db)):
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

@router.post('/create-manager')
async def create_manager(mg: portal_schemas.ManagerPayload, db: AsyncSession = Depends(get_db)):
    try:
        existing = await crud.get_manager_by_email(db, mg.email)
    except SQLAlchemyError:
         raise HTTPException(status_code=500, detail=f"Failed to get manager information from email {mg.email}")

    if existing:
        raise HTTPException(status_code=400, detail="Manager exists")

    try:
        manager = create_manager(mg, db)
        return manager
    except SQLAlchemyError:
         HTTPException(status_code=500, detail="Internal server error inserting manager into the database")
