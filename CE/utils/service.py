from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_
from datetime import datetime
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.sql.sqltypes import Integer, Float, Boolean, DateTime, String
from sqlmodel import SQLModel
from connections.redis import RedisClient
import json

class BaseService:
    def __init__(self, model: SQLModel):
        self.model = model
        self.cache_prefix = f"{model.__tablename__}"

    def _build_cache_field(self, filters):
        return f"{json.dumps(filters or {}, sort_keys=True)}"

    async def invalidate_cache(self, redis_client: RedisClient = None):
        if redis_client:
            print(f"Invalidating cache for {self.cache_prefix}")
            await redis_client.delete(self.cache_prefix)

    async def get(
        self,
        session: AsyncSession,
        filters: Dict = None,
        redis_client: RedisClient = None
    ) -> List[Any]:
        try:

            if redis_client:
                redis_key = self.cache_prefix
                field = self._build_cache_field(filters)

                cached = await redis_client.hget(redis_key, field)
                if cached:
                    cache_data = json.loads(cached)
                    print(f"Cache hit for {redis_key}:{field} === {cache_data}")
                    return cache_data

            query = select(self.model)
            query = self._apply_filters(query, filters)

            result = await session.execute(query)
            data = result.scalars().all()
            serialized_data = jsonable_encoder(data)

            if redis_client:
                await redis_client.hset(redis_key, field, serialized_data)

            return data
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def create(self, session: AsyncSession, data: List[Dict], redis_client: RedisClient = None) -> List[Any]:
        try:
            objs = [self.model(**item) for item in data]

            session.add_all(objs)
            await session.commit()

            for obj in objs:
                await session.refresh(obj)

            await self.invalidate_cache(redis_client)
            return objs
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def update(
        self,
        session: AsyncSession,
        filters: Dict,
        values: Dict,
        redis_client: RedisClient = None
    ) -> int:
        try:

            query = update(self.model)
            query = self._apply_filters(query, filters)

            query = query.values(**values, UPDATED_AT=datetime.utcnow())

            result = await session.execute(query)
            await session.commit()

            await self.invalidate_cache(redis_client)
            return result.rowcount
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def delete(self, session: AsyncSession, filters: Dict, redis_client: RedisClient = None) -> int:
        try:
            query = delete(self.model)
            query = self._apply_filters(query, filters)

            result = await session.execute(query)
            await session.commit()

            await self.invalidate_cache(redis_client)
            return result.rowcount
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    def cast_value(self, field: str, value):
        try:
            column = getattr(self.model, field).property.columns[0]
            column_type = column.type

            if isinstance(value, list):
                return [self.cast_single_value(column_type, field, v) for v in value]

            return self.cast_single_value(column_type, field, value)

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid value for field '{field}': {value} ({str(e)})"
            )


    def cast_single_value(self, column_type, field: str, value):
        try:
            if isinstance(column_type, Integer):
                return int(value)

            if isinstance(column_type, Float):
                return float(value)

            if isinstance(column_type, Boolean):
                if isinstance(value, bool):
                    return value
                val = str(value).lower()
                if val in {"true", "1", "yes"}:
                    return True
                if val in {"false", "0", "no"}:
                    return False
                raise ValueError()

            if isinstance(column_type, DateTime):
                return datetime.fromisoformat(value)

            if isinstance(column_type, String):
                return str(value)

            return value

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid value for field '{field}': {value} ({str(e)})"
            )

    def _apply_filters(self, query, filters: dict):
        if not filters:
            return query

        conditions = []

        allowed_ops = {"eq", "ne", "gt", "gte", "lt", "lte", "in", "like", "ilike"}

        for key, value in filters.items():
            if "__" in key:
                field, op = key.split("__", 1)
            else:
                field, op = key, "eq"

            if not hasattr(self.model, field):
                raise HTTPException(status_code=400, detail=f"Invalid filter field: {field}")

            column = getattr(self.model, field)

            if op not in allowed_ops:
                raise HTTPException(status_code=400, detail=f"Invalid operator: {op}")

            try:
                if op == "in":
                    if isinstance(value, str):
                        value = value.split(",")
                    value = self.cast_value(field, value)
                else:
                    value = self.cast_value(field, value)
            except Exception:
                raise HTTPException(status_code=400, detail=f"Invalid value for field: {field}")

            if op == "eq":
                conditions.append(column == value)
            elif op == "ne":
                conditions.append(column != value)
            elif op == "gt":
                conditions.append(column > value)
            elif op == "gte":
                conditions.append(column >= value)
            elif op == "lt":
                conditions.append(column < value)
            elif op == "lte":
                conditions.append(column <= value)
            elif op == "in":
                conditions.append(column.in_(value))
            elif op == "like":
                conditions.append(column.like(value))
            elif op == "ilike":
                conditions.append(column.ilike(value))

        if conditions:
            query = query.where(and_(*conditions))

        return query