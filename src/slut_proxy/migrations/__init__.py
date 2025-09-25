import anyio_sqlite

import importlib

EXPECTED_DB_VERSION = 0

async def do_migration(con: anyio_sqlite.Connection):  # pyright: ignore[reportMissingTypeArgument]
    version: int = -1
    # check for version
    async with await con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='migrations'") as cur:
        if (await cur.fetchone()) != None:
            async with await con.execute("SELECT version FROM migrations ORDER BY version DESC") as cur:
                # there will always be 1 here so it'll be fiiiine
                res = await cur.fetchone()
                if res:
                    version = res[0]
    
    if EXPECTED_DB_VERSION == version:
        return
    
    print(f"Current DB version is {version}, need to upgrade to {EXPECTED_DB_VERSION}")
    
    for new_version in range(version + 1, EXPECTED_DB_VERSION + 1):
        print(f"Running migration {new_version}")
        mod = importlib.import_module(f"slut_proxy.migrations.{new_version}")
        _ = await con.execute("begin")
        try:
            await mod.do_migration(con)
            _ = await con.execute(f"INSERT INTO migrations (version) VALUES ({new_version})")
            _ = await con.commit()
        except:
            print(f"Failed to do transaction {new_version}!")
            _ = await con.rollback()
            exit()