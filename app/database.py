# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect
import redis.asyncio as redis

# Asynchronous PostgreSQL Database URL
DATABASE_URL = "postgresql+asyncpg://postgres:oluchi@localhost/mydb"

Base = declarative_base()

# Create async engine and sessionmaker
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Redis client for async interactions
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Function to create the tables if they don't exist
async def create_tables():
    async with engine.begin() as conn:  # Use async connection
        # Use run_sync to call synchronous operations like inspect
        await conn.run_sync(Base.metadata.create_all)

        # Example of using inspect via run_sync to check for the existence of tables
        def check_tables(sync_conn):
            inspector = inspect(sync_conn)
            if not inspector.has_table("items"):
                Base.metadata.create_all(sync_conn)

        # Run the sync operation in the async context
        await conn.run_sync(check_tables)

# Dependency to get async DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
