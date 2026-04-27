import asyncio
import asyncpg

async def create_database():
    try:
        # Connect to the default 'postgres' database
        conn = await asyncpg.connect(user='postgres', password='lok@king7', host='localhost', port=5432, database='postgres')
        
        # Check if wellnessvision exists
        result = await conn.fetch("SELECT datname FROM pg_database WHERE datname = 'wellnessvision'")
        
        if not result:
            print("Creating database 'wellnessvision'...")
            # We must execute CREATE DATABASE outside of a transaction block
            await conn.execute("CREATE DATABASE wellnessvision")
            print("Database 'wellnessvision' created successfully!")
        else:
            print("Database 'wellnessvision' already exists!")
            
        await conn.close()
    except Exception as e:
        print(f"Error creating database: {e}")

if __name__ == "__main__":
    asyncio.run(create_database())
