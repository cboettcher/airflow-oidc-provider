"""
Copyright 2026 Forschungszentrum Jülich GmbH

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import logging
from typing import Annotated

from airflow.api_fastapi.app import get_auth_manager
from airflow.api_fastapi.auth.managers.base_auth_manager import COOKIE_NAME_JWT_TOKEN
from airflow.api_fastapi.common.router import AirflowRouter
from airflow.api_fastapi.core_api.security import get_user
from airflow.providers.common.compat.sdk import conf
from authlib.common.urls import add_params_to_uri
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
    return await oidc_client.authorize_redirect(
        request, redirect_uri, claims_in_tokens="id_token token"
    )  # TODO extra options need to be configured in the airflow settings and not hard coded!


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
async def logout(request: Request, user: Annotated[OIDCAuthManagerUser, Depends(get_user)]):
    redirect_url = conf.get("api", "base_url", fallback="/")
    auth_manager = get_auth_manager()
    id_token = request.cookies.get(COOKIE_NAME_ID_TOKEN)
    response = None

    if auth_manager.is_provider_logout_enabled():  # type: ignore[attr-defined]
        logout_url = auth_manager.get_provider_logout_url()  # type: ignore[attr-defined]
        if logout_url:
            params = {
                "post_logout_redirect_uri": auth_manager.get_post_logout_redirect_uri()  # type: ignore[attr-defined]
            }
            if id_token:
                params["id_token_hint"] = id_token
            redirect_url = add_params_to_uri(logout_url, params)
        else:
            logout_kwargs = {
                "post_logout_redirect_uri": auth_manager.get_post_logout_redirect_uri()  # type: ignore[attr-defined]
            }
            if id_token:
                logout_kwargs["id_token_hint"] = id_token
            response = await auth_manager.get_oidc_client().logout_redirect(  # type: ignore[attr-defined]
                request,
                **logout_kwargs,
            )

    if response is None:
        response = RedirectResponse(url=redirect_url)
    secure = bool(conf.get("api", "ssl_cert", fallback=""))

    # end user session by deleting token cookies
    response.delete_cookie(COOKIE_NAME_JWT_TOKEN, secure=secure, httponly=True)
    response.delete_cookie(COOKIE_NAME_ID_TOKEN, secure=secure, httponly=True)

    return response
