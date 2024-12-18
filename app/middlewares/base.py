from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import Scope, Receive, Send

ERROR_MESSAGE = "No response returned."


class BaseMiddleware(BaseHTTPMiddleware):
    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        try:
            await super().__call__(scope=scope, receive=receive, send=send)
        except RuntimeError as error:
            if str(error) == ERROR_MESSAGE:
                request = Request(scope=scope, receive=receive)
                if await request.is_disconnected():
                    return
            raise

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        raise NotImplementedError
