from connections.redis import RedisClientRegistry
from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.exceptions import HTTPException
from .schemas import FloorFilter, FloorUpdate, FloorCreate, FloorRead
from connections.sqlite import get_core_session
from .service import FloorService   
from typing import List

floor_router = APIRouter()
floor_service = FloorService()

@floor_router.get("/", response_model=List[FloorRead], status_code=status.HTTP_200_OK)
async def get_floors(
    filters: FloorFilter = Depends(),
    session: AsyncSession = Depends(get_core_session),
    redis_client = Depends(RedisClientRegistry.get_db_client)
) -> List[FloorRead]:
    
    filter_dict = filters.model_dump(exclude_none=True)
    return await floor_service.get_floors(session, filter_dict, redis_client)

@floor_router.post("/", response_model=List[FloorRead], status_code=status.HTTP_201_CREATED)
async def create_floor(
    floor_data: List[FloorCreate],
    session: AsyncSession = Depends(get_core_session),
    redis_client = Depends(RedisClientRegistry.get_db_client)
) -> List[FloorRead]:

    new_floors = await floor_service.create_floor(session, floor_data, redis_client)
    return new_floors


@floor_router.patch("/", response_model=List[FloorRead], status_code=status.HTTP_200_OK)
async def update_floor(
    floor_data: FloorUpdate, 
    filters: FloorFilter = Depends(), 
    session: AsyncSession = Depends(get_core_session),
    redis_client = Depends(RedisClientRegistry.get_db_client)
    ) -> List[FloorRead]:

    filter_dict = filters.model_dump(exclude_none=True)
    updated_floor = await floor_service.update_floor(session, filter_dict, floor_data, redis_client)
    if not updated_floor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Floor not found")
    return updated_floor 


@floor_router.delete("/", response_model=List[FloorRead], status_code=status.HTTP_200_OK)
async def delete_floor(
    filters: FloorFilter = Depends(), 
    session: AsyncSession = Depends(get_core_session),
    redis_client = Depends(RedisClientRegistry.get_db_client)
    ) -> List[FloorRead]:

    filter_dict = filters.model_dump(exclude_none=True)
    floor = await floor_service.delete_floor(session, filter_dict, redis_client)
    if not floor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Floor not found")
    return floor