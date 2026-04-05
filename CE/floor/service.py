from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Floor
from .schemas import FloorCreate, FloorUpdate, FloorRead
from sqlmodel import delete, select
from typing import List, Optional

class FloorService:
    async def get_all_floor(self, session: AsyncSession) -> List[FloorRead]:
        result = await session.execute(select(Floor))
        floor = result.scalars().all()
        return floor

    async def get_floor_by_id(self, session: AsyncSession, floor_id: str) -> Optional[FloorRead]:
        result = await session.execute(select(Floor).where(Floor.FLOOR_ID == floor_id))
        floor = result.scalars().first()
        return floor

    async def create_floor(self, session: AsyncSession, floor_data: List[FloorCreate]) -> List[FloorRead]:
        new_floors = []
        for floor in floor_data:
            floor_dict = floor.model_dump()
            new_floor = Floor(**floor_dict)
            new_floor.TARGET = f"/{new_floor.TARGET}/{new_floor.FLOOR_ID}"
            session.add(new_floor)
            new_floors.append(new_floor)

        await session.commit()

        for new_floor in new_floors:
            await session.refresh(new_floor)

        return new_floors
    
    async def update_floor(self, session: AsyncSession, floor_id: str, floor_data: FloorUpdate) -> Optional[FloorRead]:
        floor = await self.get_floor_by_id(session, floor_id)
        if not floor:
            return None

        floor_data_dict = floor_data.model_dump(exclude_unset=True)
        for key, value in floor_data_dict.items():
            setattr(floor, key, value)

        floor.UPDATED_AT = datetime.utcnow()
        await session.commit()
        await session.refresh(floor)
        return floor

    async def delete_floor(self, session: AsyncSession, floor_id: str) -> Optional[FloorRead]:
        floor = await self.get_floor_by_id(session, floor_id)
        if not floor:
            return None

        await session.delete(floor)
        await session.commit()
        return floor

    async def delete_all_floor(self, session: AsyncSession) -> List[FloorRead]:
        floors = await self.get_all_floor(session)
        await session.execute(delete(Floor))
        await session.commit()    
        return floors