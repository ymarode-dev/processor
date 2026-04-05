from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Room
from .schemas import RoomCreate, RoomUpdate, RoomRead
from sqlmodel import delete, select
from typing import List, Optional

class RoomService:
    async def get_all_room(self, session: AsyncSession) -> List[RoomRead]:
        result = await session.execute(select(Room))
        room = result.scalars().all()
        return room

    async def get_room_by_id(self, session: AsyncSession, room_id: str) -> Optional[RoomRead]:
        result = await session.execute(select(Room).where(Room.ROOM_ID == room_id))
        room = result.scalars().first()
        return room

    async def create_room(self, session: AsyncSession, room_data: List[RoomCreate]) -> List[RoomRead]:
        new_rooms = []
        for room in room_data:
            room_dict = room.model_dump()
            new_room = Room(**room_dict)
            new_room.TARGET = f"/{new_room.TARGET}/{new_room.ROOM_ID}"
            session.add(new_room)
            new_rooms.append(new_room)

        await session.commit()

        for new_room in new_rooms:
            await session.refresh(new_room)

        return new_rooms

    async def update_room(self, session: AsyncSession, room_id: str, room_data: RoomUpdate) -> Optional[RoomRead]:
        room = await self.get_room_by_id(session, room_id)
        if not room:
            return None

        room_data_dict = room_data.model_dump(exclude_unset=True)
        for key, value in room_data_dict.items():
            setattr(room, key, value)

        room.UPDATED_AT = datetime.utcnow()
        await session.commit()
        await session.refresh(room)
        return room

    async def delete_room(self, session: AsyncSession, room_id: str) -> Optional[RoomRead]:
        room = await self.get_room_by_id(session, room_id)
        if not room:
            return None

        await session.delete(room)
        await session.commit()
        return room

    async def delete_all_room(self, session: AsyncSession) -> List[RoomRead]:
        rooms = await self.get_all_room(session)
        await session.execute(delete(Room))
        await session.commit()    
        return rooms