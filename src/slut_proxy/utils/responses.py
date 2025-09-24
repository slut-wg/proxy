from typing_extensions import override
import msgspec
from starlette.responses import JSONResponse

class MsgspecJSONResponse(JSONResponse):
    @override
    def render(self, content: msgspec.Struct) -> bytes:
        return msgspec.json.encode(content)