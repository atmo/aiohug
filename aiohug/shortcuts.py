import json
from typing import Any, Optional

from aiohttp import web
from aiohttp.typedefs import JSONEncoder, LooseHeaders
from aiohttp.web_response import Response

RESPONSE_STATUS = 0
RESPONSE_BODY = 1

sentinel: Any = object()


# copy from aiohttp.web_response with ability to configure charset and `content_type` parameter with default set to None
def json_response(
    data: Any = sentinel,
    *,
    text: str = None,
    body: bytes = None,
    status: int = 200,
    reason: Optional[str] = None,
    headers: LooseHeaders = None,
    content_type: Optional[str] = None,
    charset: Optional[str] = None,
    dumps: JSONEncoder = json.dumps
) -> Response:
    if data is not sentinel:
        if text or body:
            raise ValueError("only one of data, text, or body should be specified")
        else:
            text = dumps(data)

    if content_type is None:
        content_type = "application/json"

    return Response(
        text=text, body=body, status=status, reason=reason, headers=headers, content_type=content_type, charset=charset
    )


def process_response(resp, output=None):
    if isinstance(resp, web.Response):
        # No shortcuts needed, manual override
        return resp

    content_type = output and output.content_type or None
    charset = output and output.charset or None

    # plain text
    if type(resp) is str:
        return web.Response(text=resp, content_type=content_type, charset=charset)

    # json
    elif type(resp) is dict or type(resp) is list:
        return json_response(data=resp, content_type=content_type, charset=charset)

    # status and body
    elif (
        type(resp) is tuple
        and type(resp[RESPONSE_STATUS]) is int
        and (type(resp[RESPONSE_BODY]) is dict or type(resp[RESPONSE_BODY]) is list)
    ):
        return json_response(
            status=resp[RESPONSE_STATUS], data=resp[RESPONSE_BODY], content_type=content_type, charset=charset
        )

    # No shortcuts found, do the best we can
    return web.Response(text=str(resp), content_type=content_type, charset=charset)
