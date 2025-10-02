from typing import Any
from typing_extensions import override
import msgspec
from starlette.responses import JSONResponse

class MsgspecJSONResponse(JSONResponse):
    _content: msgspec.Struct

    @override
    def __init__(
        self,
        content: Any,
        status_code: int = 200,
        headers: dict[str, str] | None = None,
        media_type: str | None = None,
        background: Any | None = None,
    ) -> None:
        self._content = content
        super().__init__(content, status_code, headers, media_type, background)

    @override
    def render(self, content: msgspec.Struct) -> bytes:
        return msgspec.json.encode(content)
