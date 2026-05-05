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
from typing import Any
from typing import Literal
from urllib.parse import urljoin

from airflow.api_fastapi.app import AUTH_MANAGER_FASTAPI_APP_PREFIX
from airflow.api_fastapi.auth.managers.base_auth_manager import BaseAuthManager
from airflow.api_fastapi.auth.managers.models.resource_details import AccessView
from airflow.api_fastapi.auth.managers.models.resource_details import AssetAliasDetails
from airflow.api_fastapi.auth.managers.models.resource_details import AssetDetails
from airflow.api_fastapi.auth.managers.models.resource_details import BackfillDetails
from airflow.api_fastapi.auth.managers.models.resource_details import (
    ConfigurationDetails,
)
from airflow.api_fastapi.auth.managers.models.resource_details import ConnectionDetails
from airflow.api_fastapi.auth.managers.models.resource_details import DagAccessEntity
from airflow.api_fastapi.auth.managers.models.resource_details import DagDetails
from airflow.api_fastapi.auth.managers.models.resource_details import PoolDetails
from airflow.api_fastapi.auth.managers.models.resource_details import TeamDetails
from airflow.api_fastapi.auth.managers.models.resource_details import VariableDetails
from airflow.api_fastapi.common.types import MenuItem
from airflow.providers.common.compat.sdk import conf
from authlib.integrations.starlette_client import OAuth
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from airflow_oidc_provider.auth_manager.constants import CONF_CLIENT_ID_KEY
from airflow_oidc_provider.auth_manager.constants import CONF_CLIENT_SECRET_KEY
from airflow_oidc_provider.auth_manager.constants import CONF_SCOPES
from airflow_oidc_provider.auth_manager.constants import CONF_SCOPES_DEFAULT
from airflow_oidc_provider.auth_manager.constants import CONF_SECTION_NAME
from airflow_oidc_provider.auth_manager.constants import CONF_SERVER_URL_KEY
from airflow_oidc_provider.auth_manager.token_parser import get_token_parser
from airflow_oidc_provider.auth_manager.user import OIDCAuthManagerUser

log = logging.getLogger(__name__)

IDP_INTERNAL_NAME = "idp"


class OIDCAuthManager(BaseAuthManager[OIDCAuthManagerUser]):
    def __init__(self, context=None):
        super().__init__(context)
        client_id = conf.get(CONF_SECTION_NAME, CONF_CLIENT_ID_KEY)
        client_secret = conf.get(CONF_SECTION_NAME, CONF_CLIENT_SECRET_KEY)
        server_url = conf.get(CONF_SECTION_NAME, CONF_SERVER_URL_KEY)
        scopes = conf.get(CONF_SECTION_NAME, CONF_SCOPES, CONF_SCOPES_DEFAULT)
        self.oauth_registry = OAuth()
        self.oauth_registry.register(
            name=IDP_INTERNAL_NAME,
            client_id=client_id,
            client_secret=client_secret,
            server_metadata_url=server_url,
            client_kwargs={"scope": scopes},
        )
        log.info("Registered OIDC Provider")

    def is_authorized_configuration(
        self,
        *,
        method: Literal["GET"] | Literal["POST"] | Literal["PUT"] | Literal["DELETE"],
        user: OIDCAuthManagerUser,
        details: ConfigurationDetails | None = None,
    ) -> bool:
        if method == "GET":
            return user.is_viewer()
        return user.is_operator()

    def is_authorized_connection(
        self,
        *,
        method: Literal["GET"] | Literal["POST"] | Literal["PUT"] | Literal["DELETE"],
        user: OIDCAuthManagerUser,
        details: ConnectionDetails | None = None,
    ) -> bool:
        if method == "GET":
            return user.is_user(details.team_name if details else None)
        return user.is_operator(details.team_name if details else None)

    def is_authorized_dag(
        self,
        *,
        method: Literal["GET"] | Literal["POST"] | Literal["PUT"] | Literal["DELETE"],
        user: OIDCAuthManagerUser,
        access_entity: DagAccessEntity | None = None,
        details: DagDetails | None = None,
    ) -> bool:
        return self._is_authorized_default(
            method=method, user=user, team_name=details.team_name if details else None
        )

    def is_authorized_backfill(
        self,
        *,
        method: Literal["GET"] | Literal["POST"] | Literal["PUT"] | Literal["DELETE"],
        user: OIDCAuthManagerUser,
        details: BackfillDetails | None = None,
    ) -> bool:
        return self._is_authorized_default(method=method, user=user)

    def is_authorized_asset(
        self,
        *,
        method: Literal["GET"] | Literal["POST"] | Literal["PUT"] | Literal["DELETE"],
        user: OIDCAuthManagerUser,
        details: AssetDetails | None = None,
    ) -> bool:
        return self._is_authorized_default(method=method, user=user)

    def is_authorized_asset_alias(
        self,
        *,
        method: Literal["GET"] | Literal["POST"] | Literal["PUT"] | Literal["DELETE"],
        user: OIDCAuthManagerUser,
        details: AssetAliasDetails | None = None,
    ) -> bool:
        return self._is_authorized_default(method=method, user=user)

    def is_authorized_pool(
        self,
        *,
        method: Literal["GET"] | Literal["POST"] | Literal["PUT"] | Literal["DELETE"],
        user: OIDCAuthManagerUser,
        details: PoolDetails | None = None,
    ) -> bool:
        return user.is_operator(details.team_name if details else None)

    def is_authorized_variable(
        self,
        *,
        method: Literal["GET"] | Literal["POST"] | Literal["PUT"] | Literal["DELETE"],
        user: OIDCAuthManagerUser,
        details: VariableDetails | None = None,
    ) -> bool:
        return user.is_operator(details.team_name if details else None)

    def is_authorized_view(self, *, access_view: AccessView, user: OIDCAuthManagerUser) -> bool:
        return user.is_viewer()

    def is_authorized_custom_view(
        self,
        *,
        method: str | Literal["GET"] | Literal["POST"] | Literal["PUT"] | Literal["DELETE"],
        resource_name: str,
        user: OIDCAuthManagerUser,
    ) -> bool:
        return self._is_authorized_default(method=method, user=user)

    def filter_authorized_menu_items(
        self, menu_items: list[MenuItem], *, user: OIDCAuthManagerUser
    ) -> list[MenuItem]:
        return list(menu_items or [])

    # def is_authorized_hitl_task(
    #    self, *, assigned_users: set[str], user: OIDCAuthManagerUser
    # ) -> bool:
    #    return (
    #        user.get_id() in assigned_users or user.get_name() in assigned_users or user.is_admin()
    #    )  # TODO doesn't seem like a good idea, since per-user access isnt used anywhere else. possible make it USER or OPERATOR level instead

    def is_authorized_team(
        self,
        *,
        method: Literal["GET"] | Literal["POST"] | Literal["PUT"] | Literal["DELETE"],
        user: OIDCAuthManagerUser,
        details: TeamDetails | None = None,
    ) -> bool:
        if method == "GET":
            return user.is_viewer(details.name if details else None)
        return user.is_operator(details.name if details else None)

    def _is_authorized_default(
        self,
        method: str | Literal["GET"] | Literal["POST"] | Literal["PUT"] | Literal["DELETE"],
        user: OIDCAuthManagerUser,
        team_name: str | None = None,
    ) -> bool:
        """
        Return Readonly access for viewers and everything else for users per default.

        :param self: Description
        :param method: Description
        :type method: str | Literal['GET'] | Literal['POST'] | Literal['PUT'] | Literal['DELETE']
        :param user: Description
        :type user: OIDCAuthManagerUser
        :return: Description
        :rtype: bool
        """
        if method == "GET":
            return user.is_viewer(team_name)
        return user.is_user(team_name)

    # def refresh_user(self, *, user: OIDCAuthManagerUser) -> OIDCAuthManagerUser | None:
    # TODO
    # return super().refresh_user(*, user=user)

    def get_oidc_client(self):
        return self.oauth_registry.create_client(IDP_INTERNAL_NAME)

    def deserialize_user(self, token: dict[str, Any]) -> OIDCAuthManagerUser:
        return OIDCAuthManagerUser(
            user_id=token.pop("user_id"),
            name=token.pop("name"),
            teams=token.pop("teams"),
            is_admin=token.pop("admin"),
        )

    def serialize_user(self, user: OIDCAuthManagerUser) -> dict[str, Any]:
        return {
            "user_id": user.get_id(),
            "name": user.get_name(),
            "teams": user.teams,
            "admin": user.admin,
        }

    def get_url_login(self, **kwargs) -> str:
        base_url = conf.get("api", "base_url", fallback="/")
        return urljoin(base_url, f"{AUTH_MANAGER_FASTAPI_APP_PREFIX}/login")

    def get_url_logout(self) -> str | None:
        base_url = conf.get("api", "base_url", fallback="/")
        return urljoin(base_url, f"{AUTH_MANAGER_FASTAPI_APP_PREFIX}/logout")

    def get_fastapi_app(self) -> FastAPI | None:
        from airflow_oidc_provider.auth_manager.routes.login import login_router

        app = FastAPI(
            title="OIDC auth manager sub application",
            description=(
                "This is the OIDC auth manager sub application for fastAPI."
                "It is only available if the OIDC auth manager is used in the Airflow environment."
                "It only provides login routes."
            ),
        )
        app.include_router(login_router)
        app.add_middleware(SessionMiddleware, secret_key="some-random-string")

        return app

    def _get_teams(self) -> set[str]:
        return get_token_parser().get_teams_from_config()  # TODO do this in its own config
