import asyncio
import asyncpg
from pathlib import Path
from app.core.config import settings


async def run_migrations():
    """Run all pending migrations"""
    conn = await asyncpg.connect(settings.database_url)
    
    try:
        # Create migrations tracking table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version VARCHAR(255) PRIMARY KEY,
                applied_at TIMESTAMPTZ DEFAULT now()
            )
        """)
        
        # Get applied migrations
        applied = await conn.fetch("SELECT version FROM schema_migrations")
        applied_versions = {row['version'] for row in applied}
        
        # Get migration files
        migrations_dir = Path(__file__).parent / "migrations"
        migration_files = sorted(migrations_dir.glob("*.sql"))
        
        for migration_file in migration_files:
            version = migration_file.stem
            if version in applied_versions:
                print(f"Migration {version} already applied, skipping...")
                continue
            
            print(f"Applying migration {version}...")
            sql = migration_file.read_text(encoding='utf-8')
            
            async with conn.transaction():
                await conn.execute(sql)
                await conn.execute(
                    "INSERT INTO schema_migrations (version) VALUES ($1)",
                    version
                )
            
            print(f"Migration {version} applied successfully!")
        
        print("All migrations completed!")
        
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(run_migrations())

