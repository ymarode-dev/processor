from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Property
from .schemas import PropertyCreate, PropertyUpdate, PropertyRead
from sqlmodel import select
from typing import Optional

class PropertyService:
    async def get_property(self, session: AsyncSession) -> PropertyRead:
        result = await session.execute(select(Property))
        property = result.scalars().first()
        return property

    async def create_property(self, session: AsyncSession, property_data: PropertyCreate) -> PropertyRead:
        property_data_dict = property_data.model_dump()
        new_property = Property(**property_data_dict)
        new_property.TARGET = f"/{new_property.PROPERTY_ID}"
        session.add(new_property)
        await session.commit()
        await session.refresh(new_property)
        return new_property

    async def update_property(self, session: AsyncSession, property_data: PropertyUpdate) -> Optional[PropertyRead]:
        property_to_update = await self.get_property(session)

        if not property_to_update:
            return None

        property_data_dict = property_data.model_dump(exclude_unset=True)

        for key, value in property_data_dict.items():
            setattr(property_to_update, key, value)

        property_to_update.UPDATED_AT = datetime.utcnow()

        await session.commit()
        await session.refresh(property_to_update)
        return property_to_update

    async def delete_property(self, session: AsyncSession) -> bool:
        property_to_delete = await self.get_property(session)

        if not property_to_delete:
            return False

        await session.delete(property_to_delete)
        await session.commit()
        return True
