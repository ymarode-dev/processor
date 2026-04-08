from connections.redis import RedisClientRegistry
from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.exceptions import HTTPException
from .schemas import PropertyFilter, PropertyRead, PropertyCreate, PropertyUpdate
from connections.sqlite import get_core_session
from .service import PropertyService   
from typing import List

property_router = APIRouter()
property_service = PropertyService()

@property_router.get("/", response_model=List[PropertyRead], status_code=status.HTTP_200_OK)
async def get_properties(
    filters: PropertyFilter = Depends(),
    session: AsyncSession = Depends(get_core_session),
    redis_client = Depends(RedisClientRegistry.get_db_client)
) -> List[PropertyRead]:
    
    filter_dict = filters.model_dump(exclude_none=True)
    return await property_service.get_property(session, filter_dict, redis_client)

@property_router.post("/", response_model=List[PropertyRead], status_code=status.HTTP_201_CREATED)
async def create_property(
    property_data: List[PropertyCreate],
    session: AsyncSession = Depends(get_core_session),
    redis_client = Depends(RedisClientRegistry.get_db_client)
) -> List[PropertyRead]:

    new_properties = await property_service.create_property(session, property_data, redis_client)
    return new_properties

@property_router.patch("/", response_model=List[PropertyRead], status_code=status.HTTP_200_OK)
async def update_property(
    property_data: PropertyUpdate, 
    filters: PropertyFilter = Depends(), 
    session: AsyncSession = Depends(get_core_session),
    redis_client = Depends(RedisClientRegistry.get_db_client)
    ) -> List[PropertyRead]:

    filter_dict = filters.model_dump(exclude_none=True)
    updated_property = await property_service.update_property(session, filter_dict, property_data, redis_client)
    if not updated_property:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")
    return updated_property 


@property_router.delete("/", response_model=List[PropertyRead], status_code=status.HTTP_200_OK)
async def delete_property(
    filters: PropertyFilter = Depends(), 
    session: AsyncSession = Depends(get_core_session),
    redis_client = Depends(RedisClientRegistry.get_db_client)
    ) -> List[PropertyRead]:

    filter_dict = filters.model_dump(exclude_none=True)
    property = await property_service.delete_property(session, filter_dict, redis_client)
    if not property:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")
    return property