import pytest

try:
    from tests_common.test_utils.config import conf_vars

    CONF_VARS_PRESENT = True
except:  # noqa E901,E722
    CONF_VARS_PRESENT = False

from airflow_oidc_provider.auth_manager.constants import CONF_SECTION_NAME
from airflow_oidc_provider.auth_manager.constants import CONF_TOKEN_PARSER_CLASS
from airflow_oidc_provider.auth_manager.constants import CONF_TOKEN_PARSER_CONFIG
from airflow_oidc_provider.auth_manager.token_parser import SimpleOIDCTokenParser
from airflow_oidc_provider.auth_manager.token_parser import get_token_parser
from airflow_oidc_provider.auth_manager.user import OIDCAuthManagerUser


@pytest.fixture
def simple_parser_config():
    yield """{
          "token_key" : "token_key",
          "admin_group" : "admin",
          "teams" : {
              "Team 1" : {
                  "team1:operator" : "operator",
                  "team1:user" : "user"
              },
              "Fantasy Organization" : {
                    "fantastic:department:support" : "operator",
                    "cooperation_partner:staff" : "viewer",
                    "fantastic:staff" : "user"
              }
          }
        }"""


@pytest.fixture
def token_parser(simple_parser_config):
    if not CONF_VARS_PRESENT:  # workaround
        yield SimpleOIDCTokenParser(simple_parser_config)
    # if possible, test the instance creation from airflow config
    with conf_vars(
        {
            (
                CONF_SECTION_NAME,
                CONF_TOKEN_PARSER_CLASS,
            ): "airflow_oidc_provider.auth_manager.token_parser.SimpleOIDCTokenParser",
            (CONF_SECTION_NAME, CONF_TOKEN_PARSER_CONFIG): simple_parser_config,
        }
    ):
        yield get_token_parser()


@pytest.fixture
def user_token():
    yield {
        "access_token": "place token here",
        "refresh_token": "refresh_token",
        "userinfo": {
            "key1": "somedate",
            "key2": "more data",
            "Team 1": "irrelevant Data",
            "token_key": ["Some Group", "Team 1", "team1:operator", "cooperation_partner:staff"],
            "sub": "subject name",
            "preferred_username": "username",
            "key3": "more data to be ignored by the parser",
        },
    }


def test_get_parser(token_parser):
    assert isinstance(token_parser, SimpleOIDCTokenParser)
    assert token_parser.admin_group == "admin"
    assert token_parser.token_key == "token_key"


def test_parser_teams(token_parser):
    assert isinstance(token_parser, SimpleOIDCTokenParser)
    assert "Team 1" in token_parser.teams_config
    assert "Fantasy Organization" in token_parser.teams_config

    assert token_parser.teams_config["Team 1"]["team1:user"] == "user"


def test_parse_user(token_parser, user_token):
    user = token_parser.parse(user_token)
    assert isinstance(user, OIDCAuthManagerUser)
    print(user.teams)
    assert user.access_token == "place token here"
    assert user.admin is False
    assert user.name == "username"
    assert user.refresh_token == "refresh_token"
    assert user.is_user("Team 1")
    assert user.is_viewer("Fantasy Organization")
    assert user.user_id == "subject name"
