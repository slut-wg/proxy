import secrets
import hashlib
import json
from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse
from starlette.routing import Route
from starlette.staticfiles import StaticFiles

import anyio_sqlite

from slut_proxy.models.slut import ApiKeyInfo, ApiKeyReq
from slut_proxy.models.config import Config
from slut_proxy.utils.responses import MsgspecJSONResponse

def build_routes(config: Config) -> list[Route]:
    async def admin_dashboard(request: Request) -> HTMLResponse:
        """Serve the admin dashboard HTML"""
        # Read the HTML template
        import os
        template_path = os.path.join(os.path.dirname(__file__), '../../templates/admin.html')
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            return HTMLResponse(html_content)
        except FileNotFoundError:
            return HTMLResponse("<h1>Admin dashboard template not found</h1>", status_code=500)

    async def get_api_key(request: Request) -> MsgspecJSONResponse:
        """Get information about a specific API key"""
        key = request.query_params.get("key")
        if not key:
            return JSONResponse(
                {"error": "Missing 'key' query parameter"},
                status_code=400
            )

        db: anyio_sqlite.Connection = request.state.db  # pyright: ignore[reportMissingTypeArgument, reportAny]
        
        # Hash the key for lookup
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        
        async with await db.execute(
            "SELECT full_key, key_prefix, allowed_providers, allowed_models FROM api_keys WHERE key_hash = ? AND is_active = 1",
            (key_hash,)
        ) as cur:
            row = await cur.fetchone()
            
        if not row:
            return JSONResponse(
                {"error": "API key not found"},
                status_code=404
            )
        
        api_key_info = ApiKeyInfo(
            key=row[0] if row[0] else row[1] + "...",  # Use full key if available, otherwise prefix
            allowed_providers=json.loads(row[2]),
            allowed_models=json.loads(row[3])
        )
        
        return MsgspecJSONResponse(api_key_info)

    async def list_api_keys(request: Request) -> MsgspecJSONResponse:
        """List all API keys"""
        db: anyio_sqlite.Connection = request.state.db  # pyright: ignore[reportMissingTypeArgument, reportAny]
        
        api_keys = []
        async with await db.execute(
            "SELECT full_key, key_prefix, allowed_providers, allowed_models FROM api_keys WHERE is_active = 1"
        ) as cur:
            async for row in cur:
                api_keys.append(ApiKeyInfo(
                    key=row[0] if row[0] else row[1] + "...",
                    allowed_providers=json.loads(row[2]),
                    allowed_models=json.loads(row[3])
                ))
        
        return MsgspecJSONResponse(api_keys)

    async def create_api_key(request: Request) -> JSONResponse:
        """Create a new API key"""
        body = await request.json()
        
        # Validate required fields
        if "allowed_providers" not in body or "allowed_models" not in body:
            return JSONResponse(
                {"error": "Missing required fields: allowed_providers and allowed_models"},
                status_code=400
            )
        
        db: anyio_sqlite.Connection = request.state.db  # pyright: ignore[reportMissingTypeArgument, reportAny]
        
        # Generate a proper API key
        new_key = f"sk-{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(new_key.encode()).hexdigest()
        key_prefix = new_key[:8]
        
        try:
            await db.execute(
                """INSERT INTO api_keys 
                   (key_hash, key_prefix, full_key, allowed_providers, allowed_models) 
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    key_hash,
                    key_prefix,
                    new_key,
                    json.dumps(body["allowed_providers"]),
                    json.dumps(body["allowed_models"])
                )
            )
            await db.commit()
            
            return JSONResponse(
                {"key": new_key, "message": "API key created successfully"},
                status_code=201
            )
        except anyio_sqlite.IntegrityError:
            return JSONResponse(
                {"error": "Failed to create API key - duplicate hash"},
                status_code=500
            )

    async def delete_api_key(request: Request) -> JSONResponse:
        """Delete an API key"""
        body = await request.json()
        key_req = ApiKeyReq(**body)
        
        db: anyio_sqlite.Connection = request.state.db  # pyright: ignore[reportMissingTypeArgument, reportAny]
        
        # Hash the key for lookup
        key_hash = hashlib.sha256(key_req.key.encode()).hexdigest()
        
        cursor = await db.execute(
            "SELECT full_key FROM api_keys WHERE key_hash = ? AND is_active = 1",
            (key_hash,)
        )
        row = await cursor.fetchone()
        
        if not row:
            return JSONResponse(
                {"error": "API key not found"},
                status_code=404
            )
        
        # Soft delete by setting is_active = 0
        await db.execute(
            "UPDATE api_keys SET is_active = 0 WHERE key_hash = ?",
            (key_hash,)
        )
        await db.commit()
        
        return JSONResponse(
            {"message": f"API key {row[0]} deleted successfully"},
            status_code=200
        )

    return [
        Route("/admin", admin_dashboard, methods=["GET"]),
        Route("/admin/api_keys", get_api_key, methods=["GET"]),
        Route("/admin/api_keys/list", list_api_keys, methods=["GET"]),
        Route("/admin/api_keys", create_api_key, methods=["POST"]),
        Route("/admin/api_keys", delete_api_key, methods=["DELETE"]),
    ]
