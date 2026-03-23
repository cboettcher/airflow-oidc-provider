import importlib
import json

from airflow.providers.common.compat.sdk import conf

from airflow_oidc_provider.auth_manager.constants import CONF_SECTION_NAME
from airflow_oidc_provider.auth_manager.constants import CONF_TOKEN_PARSER_CLASS
from airflow_oidc_provider.auth_manager.constants import CONF_TOKEN_PARSER_CLASS_DEFAULT
from airflow_oidc_provider.auth_manager.constants import CONF_TOKEN_PARSER_CONFIG
from airflow_oidc_provider.auth_manager.user import OIDCAuthManagerUser
from airflow_oidc_provider.auth_manager.user import OIDCUserRole


class BaseOIDCTokenParser:

    def __init__(self, parser_config: str) -> None:
        self.config = parser_config

    def parse(self, oidc_token: dict) -> OIDCAuthManagerUser:
        raise NotImplementedError

    def get_teams_from_config(self) -> set[str]:
        raise NotImplementedError


def get_token_parser() -> BaseOIDCTokenParser:
    classpath = conf.get(
        CONF_SECTION_NAME, CONF_TOKEN_PARSER_CLASS, CONF_TOKEN_PARSER_CLASS_DEFAULT
    )
    module_name, class_name = classpath.rsplit(".", 1)
    configured_parser_class = getattr(importlib.import_module(module_name), class_name)
    return configured_parser_class(conf.get(CONF_SECTION_NAME, CONF_TOKEN_PARSER_CONFIG))


class SimpleOIDCTokenParser(BaseOIDCTokenParser):

    def __init__(self, parser_config: str) -> None:
        super().__init__(parser_config)
        # store parser config in a dict with teamname and rolename as keys to easily lookup access level per team
        """
        config for this parser ist
        {
          "token_key" : "<token_key>",
          "admin_group" : "<admin_group>",
          "teams" : {
              "<team_name>" : {
                  "<group_name>" : "<OIDCUserRole>",
                  "<group_name_2>" : "<OIDCUserRole>",
                    ...
              },
              "team_name2>" : {...}.
              ...
          }
        }
        where OIDCUserRole is VIEWER, USER, OPERATOR
        therefore parse json string
        """
        config_dict = json.loads(self.config)
        self.token_key = config_dict["token_key"]
        self.admin_group = config_dict["admin_group"]
        self.teams_config: dict[str, dict[str, str]] = config_dict["teams"]

    def get_teams_from_config(self) -> set[str]:
        return set(self.teams_config.keys())

    def _get_teams(self, groups_list: list[str]) -> dict[str, int]:
        teams: dict[str, int] = {}
        for group in groups_list:
            for team in self.teams_config:
                team_role: int = OIDCUserRole[
                    self.teams_config[team].get(group, OIDCUserRole.ANONYMOUS.name).upper()
                ].value  # some shenanigans to get UserRoleValue from role name string
                if not teams.get(team, None) or teams[team] < team_role:
                    teams[team] = team_role
        return teams

    def parse(self, oidc_token: dict) -> OIDCAuthManagerUser:
        userinfo = oidc_token["userinfo"]
        user = OIDCAuthManagerUser(
            user_id=userinfo["sub"],
            name=userinfo["preferred_username"],
            teams=self._get_teams(userinfo[self.token_key]),
            is_admin=(self.admin_group in userinfo[self.token_key]),
        )
        return user
