from connections.redis import RedisClientRegistry
from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.exceptions import HTTPException
from .schemas import RoomFilter, RoomRead, RoomCreate, RoomUpdate
from connections.sqlite import get_core_session
from .service import RoomService   
from typing import List

room_router = APIRouter()
room_service = RoomService()

@room_router.get("/", response_model=List[RoomRead], status_code=status.HTTP_200_OK)
async def get_rooms(
    filters: RoomFilter = Depends(),
    session: AsyncSession = Depends(get_core_session),
    redis_client = Depends(RedisClientRegistry.get_db_client)
) -> List[RoomRead]:
    
    filter_dict = filters.model_dump(exclude_none=True)
    return await room_service.get_rooms(session, filter_dict, redis_client)


@room_router.post("/", response_model=List[RoomRead], status_code=status.HTTP_201_CREATED)
async def create_room(
    room_data: List[RoomCreate], 
    session: AsyncSession = Depends(get_core_session),
    redis_client = Depends(RedisClientRegistry.get_db_client)
    ) -> List[RoomRead]:

    new_rooms = await room_service.create_room(session, room_data, redis_client)
    return new_rooms


@room_router.patch("/", response_model=List[RoomRead], status_code=status.HTTP_200_OK)
async def update_room(
    room_data: RoomUpdate, 
    filters: RoomFilter = Depends(), 
    session: AsyncSession = Depends(get_core_session),
    redis_client = Depends(RedisClientRegistry.get_db_client)
    ) -> List[RoomRead]:

    filter_dict = filters.model_dump(exclude_none=True)
    updated_room = await room_service.update_room(session, filter_dict, room_data, redis_client)
    if not updated_room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    return updated_room   


@room_router.delete("/", response_model=List[RoomRead], status_code=status.HTTP_200_OK)
async def delete_room(
    filters: RoomFilter = Depends(), 
    session: AsyncSession = Depends(get_core_session),
    redis_client = Depends(RedisClientRegistry.get_db_client)
    ) -> List[RoomRead]:

    filter_dict = filters.model_dump(exclude_none=True)
    room = await room_service.delete_room(session, filter_dict, redis_client)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    return room