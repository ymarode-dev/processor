from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.exceptions import HTTPException
from .schemas import RoomRead, RoomCreate, RoomUpdate
from CE.connections.sqlite import get_core_session
from .service import RoomService   
from typing import List

room_router = APIRouter()
room_service = RoomService()

@room_router.get("/", response_model=List[RoomRead], status_code=status.HTTP_200_OK)
async def get_all_room(session: AsyncSession = Depends(get_core_session)) -> List[RoomRead]:
    rooms = await room_service.get_all_room(session)
    return rooms

@room_router.get("/{room_id}", response_model=RoomRead, status_code=status.HTTP_200_OK)
async def get_room_by_id(room_id: str, session: AsyncSession = Depends(get_core_session)) -> RoomRead:
    room = await room_service.get_room_by_id(session, room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    return room

@room_router.post("/", response_model=List[RoomRead], status_code=status.HTTP_201_CREATED)
async def create_room(room_data: List[RoomCreate], session: AsyncSession = Depends(get_core_session)) -> List[RoomRead]:
    new_rooms = await room_service.create_room(session, room_data)
    return new_rooms

@room_router.patch("/{room_id}", response_model=RoomRead, status_code=status.HTTP_200_OK)
async def update_room(room_id: str, room_data: RoomUpdate, session: AsyncSession = Depends(get_core_session)) -> RoomRead:
    updated_room = await room_service.update_room(session, room_id, room_data)
    if not updated_room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    return updated_room   

@room_router.delete("/{room_id}", status_code=status.HTTP_200_OK)
async def delete_room(room_id: str, session: AsyncSession = Depends(get_core_session)) -> RoomRead:
    room = await room_service.delete_room(session, room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    return room

@room_router.delete("/", status_code=status.HTTP_200_OK)
async def delete_all_room(session: AsyncSession = Depends(get_core_session)) -> List[RoomRead]:
    return await room_service.delete_all_room(session)
    