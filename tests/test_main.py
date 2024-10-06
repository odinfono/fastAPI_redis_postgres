import sys
import os
import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from fastapi import HTTPException
from app.main import app
from app.database import get_db, Base
from app import models

# Define a separate test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:oluchi@localhost/mydb_test"

# Create an async engine for the test database
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=True,
)

# Create an async sessionmaker for the test database
TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

@pytest.fixture(scope="session")
def event_loop():
    """Create a fresh event loop for the tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="function")
async def test_db():
    # Ensure operations are sequential by isolating them within context
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # Create tables

    async with TestSessionLocal() as session:
        yield session  # Yield session for use in tests

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Drop tables after tests

@pytest_asyncio.fixture(scope="function")
async def client(test_db):
    # Override the get_db dependency to use the test database
    async def override_get_db():
        try:
            yield test_db  # Use the test session in a context block
        finally:
            await test_db.close()  # Ensure session is closed

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    # Clean up the dependency override after the test
    app.dependency_overrides.pop(get_db, None)

# Test for creating an item
@pytest.mark.asyncio
async def test_create_item(client: AsyncClient):
    response = await client.post("/items/", json={"name": "Test Item", "description": "Test description"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Item"
    assert data["description"] == "Test description"

# Test for reading an item
@pytest.mark.asyncio
async def test_read_item(client: AsyncClient):
    # First, create the item
    create_response = await client.post("/items/", json={"name": "Test Item", "description": "Test description"})
    item_id = create_response.json()["id"]

    # Then, read the item
    read_response = await client.get(f"/items/{item_id}")
    assert read_response.status_code == 200
    data = read_response.json()
    assert data["name"] == "Test Item"
    assert data["description"] == "Test description"

# Test for updating an item
@pytest.mark.asyncio
async def test_update_item(client: AsyncClient):
    # Create an item
    create_response = await client.post("/items/", json={"name": "Test Item", "description": "Test description"})
    item_id = create_response.json()["id"]

    # Update the item
    update_response = await client.put(
        f"/items/{item_id}",
        json={"name": "Updated Item", "description": "Updated description"}
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["name"] == "Updated Item"
    assert data["description"] == "Updated description"

# Test for deleting an item
@pytest.mark.asyncio
async def test_delete_item(client: AsyncClient):
    # Create an item
    create_response = await client.post("/items/", json={"name": "Test Item", "description": "Test description"})
    item_id = create_response.json()["id"]

    # Delete the item
    delete_response = await client.delete(f"/items/{item_id}")
    assert delete_response.status_code == 200
    data = delete_response.json()
    assert data["id"] == item_id

    # Ensure the item is deleted
    read_response = await client.get(f"/items/{item_id}")
    assert read_response.status_code == 404
