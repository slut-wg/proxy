import anyio_sqlite

async def do_migration(con: anyio_sqlite.Connection):  # pyright: ignore[reportMissingTypeArgument]
    await con.execute("""
        CREATE TABLE api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key_hash TEXT UNIQUE NOT NULL,
            key_prefix TEXT NOT NULL,
            allowed_providers TEXT NOT NULL,
            allowed_models TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    """)
    
    # Create index for faster lookups
    await con.execute("CREATE INDEX idx_api_keys_hash ON api_keys(key_hash)")
    
    print("Created api_keys table")