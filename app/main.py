from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from . import crud, schemas
from .database import get_db, redis_client
import json
from .database import create_tables

app = FastAPI()

@app.post("/items/", response_model=schemas.Item)
async def create_item(item: schemas.ItemCreate, db: AsyncSession = Depends(get_db)):
    db_item = await crud.create_item(db=db, item=item)
    await redis_client.set(f"item_{db_item.id}", json.dumps(schemas.Item.from_orm(db_item).dict()))
    return db_item

@app.get("/items/{item_id}", response_model=schemas.Item)
async def read_item(item_id: int, db: AsyncSession = Depends(get_db)):
    cached_item = await redis_client.get(f"item_{item_id}")
    
    if cached_item:
        print("Cached Item: ", cached_item.decode('utf-8'))  # Add this for debugging
        return schemas.Item(**json.loads(cached_item.decode('utf-8')))
    
    db_item = await crud.get_item_by_id(db, item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    await redis_client.set(f"item_{item_id}", json.dumps(schemas.Item.from_orm(db_item).dict()))
    
    return db_item

@app.get("/items/", response_model=list[schemas.Item])
async def read_items(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    # Fetch all items from the database, with optional pagination (skip and limit)
    items = await crud.get_items(db, skip=skip, limit=limit)
    
    # Optionally, cache all items in Redis
    # We are not caching here since it's a list, and Redis would be better used for individual items
    return items

# Update (Edit) an item (PUT)
@app.put("/items/{item_id}", response_model=schemas.Item)
async def update_item(item_id: int, item: schemas.ItemCreate, db: AsyncSession = Depends(get_db)):
    db_item = await crud.get_item_by_id(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    updated_item = await crud.update_item(db=db, db_item=db_item, item=item)
    await redis_client.set(f"item_{item_id}", json.dumps(schemas.Item.from_orm(updated_item).dict()))
    return updated_item

# Delete an item (DELETE)
@app.delete("/items/{item_id}", response_model=schemas.Item)
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
    db_item = await crud.get_item_by_id(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    await crud.delete_item(db=db, db_item=db_item)
    await redis_client.delete(f"item_{item_id}")
    return db_item
