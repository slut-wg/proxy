import anyio_sqlite

async def do_migration(con: anyio_sqlite.Connection):  # pyright: ignore[reportMissingTypeArgument]
    _ = await con.execute("CREATE TABLE migrations (version INTEGER)")
    pass