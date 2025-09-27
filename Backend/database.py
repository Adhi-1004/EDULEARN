
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

# Database connection
client = None
db = None

async def init_db():
    """Initialize database connection"""
    global client, db
    try:
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        db_name = os.getenv("DB_NAME", "modlrn")
        
        print(f"🔧 [DB] Connecting to MongoDB...")
        print(f"   - URI: {mongo_uri[:50]}..." if len(mongo_uri) > 50 else f"   - URI: {mongo_uri}")
        print(f"   - Database: {db_name}")
        
        # Add connection pooling and timeout settings
        client = AsyncIOMotorClient(
            mongo_uri,
            maxPoolSize=10,
            minPoolSize=1,
            maxIdleTimeMS=30000,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            socketTimeoutMS=20000
        )
        db = client[db_name]
        
        # Test the connection
        print(f"🔧 [DB] Testing connection...")
        await client.admin.command('ping')
        print(f"✅ MongoDB Connected Successfully")
        return db
    except Exception as e:
        print(f"❌ MongoDB Connection Error: {str(e)}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        print(f"❌ Connection traceback: {traceback.format_exc()}")
        raise e

async def get_db():
    """Get database instance with retry logic"""
    global db, client
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            if db is None:
                print(f"🔧 [DB] Initializing database connection (attempt {attempt + 1}/{max_retries})")
                await init_db()
            else:
                print(f"🔧 [DB] Testing existing database connection (attempt {attempt + 1}/{max_retries})")
            
            # Test connection before returning
            try:
                await client.admin.command('ping')
                print(f"✅ [DB] Database connection test successful")
                return db
            except Exception as ping_error:
                print(f"❌ [DB] Database ping failed (attempt {attempt + 1}/{max_retries}): {str(ping_error)}")
                if attempt < max_retries - 1:
                    print(f"🔄 [DB] Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                else:
                    print(f"❌ [DB] All retry attempts failed, reinitializing connection")
                    # Force reinitialization on final attempt
                    db = None
                    client = None
                    await init_db()
                    return db
                    
        except Exception as e:
            print(f"❌ [DB] Database connection attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                print(f"🔄 [DB] Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                continue
            else:
                print(f"❌ [DB] All retry attempts failed")
                raise Exception(f"Database connection failed after {max_retries} attempts: {str(e)}")
    
    # This should never be reached, but just in case
    raise Exception("Database connection failed - unexpected error")

async def close_db():
    """Close database connection"""
    global client
    if client:
        client.close()
        print("🔌 MongoDB Connection Closed") 