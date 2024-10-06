from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from . import models, schemas

# Generic function to get an item by id
async def get_item_by_id(db: AsyncSession, item_id: int):
    result = await db.execute(select(models.Item).filter(models.Item.id == item_id))
    db_item = result.scalar()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

# Retrieve all items (with optional skip and limit for pagination)
async def get_items(db: AsyncSession, skip: int = 0, limit: int = 10):
    result = await db.execute(select(models.Item).offset(skip).limit(limit))
    return result.scalars().all()

# Create item
async def create_item(db: AsyncSession, item: schemas.ItemCreate):
    db_item = models.Item(name=item.name, description=item.description)
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item

# Update item
async def update_item(db: AsyncSession, db_item: models.Item, item: schemas.ItemCreate):
    db_item.name = item.name
    db_item.description = item.description
    await db.commit()
    await db.refresh(db_item)
    return db_item

# Delete item
async def delete_item(db: AsyncSession, db_item: models.Item):
    await db.delete(db_item)
    await db.commit()
