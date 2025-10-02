import anyio_sqlite

async def do_migration(con: anyio_sqlite.Connection):  # pyright: ignore[reportMissingTypeArgument]
    # Add full_key column to store complete API keys for admin access
    await con.execute("""
        ALTER TABLE api_keys 
        ADD COLUMN full_key TEXT
    """)
    
    print("Added full_key column to api_keys table")