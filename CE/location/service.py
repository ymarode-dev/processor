from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Location
from .schemas import LocationCreate, LocationUpdate, LocationRead
from sqlmodel import select
from typing import Optional

class LocationService:
    async def get_location(self, session: AsyncSession) -> LocationRead:
        result = await session.execute(select(Location))
        location = result.scalars().first()
        return location

    async def create_location(self, session: AsyncSession, location_data: LocationCreate) -> LocationRead:
        location_data_dict = location_data.model_dump()
        new_location = Location(**location_data_dict)
        session.add(new_location)
        await session.commit()
        await session.refresh(new_location)
        return new_location

    async def update_location(self, session: AsyncSession, location_data: LocationUpdate) -> Optional[LocationRead]:
        location_to_update = await self.get_location(session)

        if not location_to_update:
            return None

        location_data_dict = location_data.model_dump(exclude_unset=True)

        for key, value in location_data_dict.items():
            setattr(location_to_update, key, value)

        location_to_update.UPDATED_AT = datetime.utcnow()

        await session.commit()
        await session.refresh(location_to_update)
        return location_to_update

    async def delete_location(self, session: AsyncSession) -> bool:
        location_to_delete = await self.get_location(session)

        if not location_to_delete:
            return False

        await session.delete(location_to_delete)
        await session.commit()
        return True
