from urllib.parse import urlencode

from fastapi import Request, status
from fastapi.responses import RedirectResponse


def build_redirect_response(
    request: Request, redirect: str
) -> RedirectResponse:
    orig_request_qparam = urlencode({"next": str(request.url)})
    next_url = "{redirect_path}?{orig_request}".format(
        redirect_path=request.url_for(redirect),
        orig_request=orig_request_qparam,
    )
    return RedirectResponse(
        url=next_url, status_code=status.HTTP_303_SEE_OTHER
    )
