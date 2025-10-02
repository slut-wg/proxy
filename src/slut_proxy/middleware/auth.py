import hashlib
import json
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, admin_key: str):
        super().__init__(app)
        self.admin_key = admin_key
    
    async def dispatch(self, request: Request, call_next):
        # Skip auth for OPTIONS requests
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # Check if this is an admin endpoint
        if request.url.path.startswith("/v2/admin/"):
            auth_header = request.headers.get("authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return JSONResponse(
                    {"error": "Missing or invalid authorization header"},
                    status_code=401
                )
            
            token = auth_header[7:]  # Remove "Bearer " prefix
            if token != self.admin_key:
                return JSONResponse(
                    {"error": "Invalid admin key"},
                    status_code=403
                )
        
        # Check if this is a generate endpoint (needs API key)
        if request.url.path.startswith("/v2/generate") or request.url.path.startswith("/v1/completions"):
            auth_header = request.headers.get("authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return JSONResponse(
                    {"error": "Missing or invalid API key"},
                    status_code=401
                )
            
            api_key = auth_header[7:]  # Remove "Bearer " prefix
            
            # Validate API key against database
            db = request.state.db  # pyright: ignore[reportMissingTypeArgument, reportAny]
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            
            async with await db.execute(
                "SELECT allowed_providers, allowed_models FROM api_keys WHERE key_hash = ? AND is_active = 1",
                (key_hash,)
            ) as cur:
                row = await cur.fetchone()
                
            if not row:
                return JSONResponse(
                    {"error": "Invalid API key"},
                    status_code=403
                )
            
            # Store the API key permissions in request state for use by endpoints
            request.state.api_key_permissions = {
                "allowed_providers": json.loads(row[0]),
                "allowed_models": json.loads(row[1])
            }
        
        return await call_next(request)
