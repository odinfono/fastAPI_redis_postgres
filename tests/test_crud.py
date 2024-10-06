import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException
from app import crud, schemas
from app.database import Base

# Use SQLite in-memory database for testing
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create a new async engine for the test database
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)

# Create a new async sessionmaker for the test database
TestSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

@pytest_asyncio.fixture(scope="function")
async def test_db():
    # Create the database tables before each test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Provide a new database session for the test
    async with TestSessionLocal() as session:
        yield session
    
    # Drop the database tables after the test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# Test case for creating an item
@pytest.mark.asyncio
async def test_create_item(test_db: AsyncSession):
    item_data = schemas.ItemCreate(name="Test Item", description="Test description")
    new_item = await crud.create_item(db=test_db, item=item_data)

    assert new_item.name == "Test Item"
    assert new_item.description == "Test description"

# Test case for reading an item by id
@pytest.mark.asyncio
async def test_get_item_by_id(test_db: AsyncSession):
    item_data = schemas.ItemCreate(name="Test Item", description="Test description")
    new_item = await crud.create_item(db=test_db, item=item_data)

    found_item = await crud.get_item_by_id(db=test_db, item_id=new_item.id)
    assert found_item.name == "Test Item"
    assert found_item.description == "Test description"

# Test case for reading multiple items
@pytest.mark.asyncio
async def test_get_items(test_db: AsyncSession):
    # Create two items
    item_data_1 = schemas.ItemCreate(name="Item 1", description="Description 1")
    item_data_2 = schemas.ItemCreate(name="Item 2", description="Description 2")
    await crud.create_item(db=test_db, item=item_data_1)
    await crud.create_item(db=test_db, item=item_data_2)

    items = await crud.get_items(db=test_db, skip=0, limit=10)
    assert len(items) == 2
    assert items[0].name == "Item 1"
    assert items[1].name == "Item 2"

# Test case for updating an item
@pytest.mark.asyncio
async def test_update_item(test_db: AsyncSession):
    item_data = schemas.ItemCreate(name="Original Item", description="Original description")
    new_item = await crud.create_item(db=test_db, item=item_data)

    update_data = schemas.ItemCreate(name="Updated Item", description="Updated description")
    updated_item = await crud.update_item(db=test_db, db_item=new_item, item=update_data)

    assert updated_item.name == "Updated Item"
    assert updated_item.description == "Updated description"

# Test case for deleting an item
@pytest.mark.asyncio
async def test_delete_item(test_db: AsyncSession):
    item_data = schemas.ItemCreate(name="Test Item", description="Test description")
    new_item = await crud.create_item(db=test_db, item=item_data)

    # Delete the item
    await crud.delete_item(db=test_db, db_item=new_item)

    # Try to retrieve the deleted item
    with pytest.raises(HTTPException) as exc_info:
        await crud.get_item_by_id(db=test_db, item_id=new_item.id)

    assert exc_info.value.status_code == 404
