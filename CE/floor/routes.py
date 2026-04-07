from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.exceptions import HTTPException
from .schemas import FloorUpdate, FloorCreate, FloorRead
from connections.sqlite import get_core_session
from .service import FloorService   
from typing import List

floor_router = APIRouter()
floor_service = FloorService()

@floor_router.get("/", response_model=List[FloorRead], status_code=status.HTTP_200_OK)
async def get_all_floor(session: AsyncSession = Depends(get_core_session)) -> List[FloorRead]:
    floors = await floor_service.get_all_floor(session)
    return floors
    
@floor_router.get("/{floor_id}", response_model=FloorRead, status_code=status.HTTP_200_OK)
async def get_floor_by_id(floor_id: str, session: AsyncSession = Depends(get_core_session)) -> FloorRead:
    floor = await floor_service.get_floor_by_id(session, floor_id)
    if not floor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Floor not found")
    return floor

@floor_router.post("/", response_model=List[FloorRead], status_code=status.HTTP_201_CREATED)
async def create_floor(floor_data: List[FloorCreate], session: AsyncSession = Depends(get_core_session)) -> List[FloorRead]:
    new_floors = await floor_service.create_floor(session, floor_data)
    return new_floors

@floor_router.patch("/{floor_id}", response_model=FloorRead, status_code=status.HTTP_200_OK)
async def update_floor(floor_id: str, floor_data: FloorUpdate, session: AsyncSession = Depends(get_core_session)) -> FloorRead:
    updated_floor = await floor_service.update_floor(session, floor_id, floor_data)
    if not updated_floor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Floor not found")
    return updated_floor   

@floor_router.delete("/{floor_id}", status_code=status.HTTP_200_OK)
async def delete_floor(floor_id: str, session: AsyncSession = Depends(get_core_session)) -> FloorRead:
    floor = await floor_service.delete_floor(session, floor_id)
    if not floor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Floor not found")
    return floor

@floor_router.delete("/", status_code=status.HTTP_200_OK)
async def delete_all_floor(session: AsyncSession = Depends(get_core_session)) -> List[FloorRead]:
    return await floor_service.delete_all_floor(session)
    