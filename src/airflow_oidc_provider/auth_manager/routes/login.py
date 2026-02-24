import logging
from typing import Annotated

from airflow.api_fastapi.app import get_auth_manager
from airflow.api_fastapi.auth.managers.base_auth_manager import COOKIE_NAME_JWT_TOKEN
from airflow.api_fastapi.common.router import AirflowRouter
from airflow.api_fastapi.core_api.security import get_user
from airflow.providers.common.compat.sdk import conf
from fastapi import Depends
from fastapi import Request
from fastapi.responses import RedirectResponse

from airflow_oidc_provider.auth_manager.token_parser import get_token_parser
from airflow_oidc_provider.auth_manager.user import OIDCAuthManagerUser

log = logging.getLogger(__name__)

login_router = AirflowRouter(tags=["OIDCAuthManagerLogin"])

COOKIE_NAME_ID_TOKEN = "_id_token"


@login_router.get("/login")
async def login(request: Request) -> RedirectResponse:
    redirect_uri = request.url_for("login_callback")
    oidc_client = get_auth_manager().get_oidc_client()  # type: ignore # can ignore, since this route only works with OIDC Auth manager anyway
    return await oidc_client.authorize_redirect(request, redirect_uri)


@login_router.get("/login_callback")
async def login_callback(request: Request):
    oidc_client = get_auth_manager().get_oidc_client()  # type: ignore
    oidc_token = await oidc_client.authorize_access_token(request)

    user = get_token_parser().parse(oidc_token=oidc_token)
    log.info(f"Created Session for user {user.get_id()} with teams {user.get_teams()}")
    airflow_token = get_auth_manager().generate_jwt(user)
    response = RedirectResponse(url=conf.get("api", "base_url", fallback="/"), status_code=303)
    secure = bool(conf.get("api", "ssl_cert", fallback=""))
    # In Airflow 3.1.1 authentication changes, front-end no longer handle the token
    # See https://github.com/apache/airflow/pull/55506
    response.set_cookie(COOKIE_NAME_JWT_TOKEN, airflow_token, secure=secure, httponly=True)
    # Save id token as separate cookie.
    # Cookies have a size limit (usually 4k), saving all the tokens in a same cookie goes beyond this limit
    response.set_cookie(COOKIE_NAME_ID_TOKEN, oidc_token["id_token"], secure=secure, httponly=True)

    return response


@login_router.get("/logout")
def logout(request: Request, user: Annotated[OIDCAuthManagerUser, Depends(get_user)]):
    response = RedirectResponse(url=conf.get("api", "base_url", fallback="/"))
    secure = bool(conf.get("api", "ssl_cert", fallback=""))

    # TODO invalidate [access|refresh]token from oidc server

    # end user session by deleting token cookies
    response.delete_cookie(COOKIE_NAME_JWT_TOKEN, secure=secure, httponly=True)
    response.delete_cookie(COOKIE_NAME_ID_TOKEN, secure=secure, httponly=True)

    return response
