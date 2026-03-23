import pytest
from airflow.api_fastapi.auth.managers.models.resource_details import AccessView
from airflow.api_fastapi.auth.managers.models.resource_details import ConnectionDetails
from airflow.api_fastapi.auth.managers.models.resource_details import PoolDetails
from airflow.api_fastapi.auth.managers.models.resource_details import TeamDetails
from airflow.api_fastapi.auth.managers.models.resource_details import VariableDetails

try:
    from tests_common.test_utils.config import conf_vars

    CONF_VARS_PRESENT = True
except:  # noqa E901,E722
    CONF_VARS_PRESENT = False

from airflow_oidc_provider.auth_manager.constants import CONF_CLIENT_ID_KEY
from airflow_oidc_provider.auth_manager.constants import CONF_CLIENT_SECRET_KEY
from airflow_oidc_provider.auth_manager.constants import CONF_SCOPES
from airflow_oidc_provider.auth_manager.constants import CONF_SECTION_NAME
from airflow_oidc_provider.auth_manager.constants import CONF_SERVER_URL_KEY
from airflow_oidc_provider.auth_manager.constants import CONF_TOKEN_PARSER_CLASS
from airflow_oidc_provider.auth_manager.constants import CONF_TOKEN_PARSER_CONFIG
from airflow_oidc_provider.auth_manager.oauth2_auth_manager import OIDCAuthManager
from airflow_oidc_provider.auth_manager.user import OIDCAuthManagerUser
from airflow_oidc_provider.auth_manager.user import OIDCUserRole


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
def auth_manager(simple_parser_config):
    with conf_vars(
        {
            (
                CONF_SECTION_NAME,
                CONF_TOKEN_PARSER_CLASS,
            ): "airflow_oidc_provider.auth_manager.token_parser.SimpleOIDCTokenParser",
            (CONF_SECTION_NAME, CONF_TOKEN_PARSER_CONFIG): simple_parser_config,
            (CONF_SECTION_NAME, CONF_CLIENT_ID_KEY): "client_id",
            (CONF_SECTION_NAME, CONF_CLIENT_SECRET_KEY): "client_secret",
            (CONF_SECTION_NAME, CONF_SERVER_URL_KEY): "https://localhost:1234/.well-known",
            (CONF_SECTION_NAME, CONF_SCOPES): "openid email extra-scope profile and so on",
        }
    ):
        yield OIDCAuthManager()


@pytest.fixture
def tmp_user():
    return OIDCAuthManagerUser(
        user_id="test_user",
        name="Test User",
        access_token="this_is_an_access_token",
        refresh_token="this_is_a_refresh_token",
        teams={
            "operator-team": OIDCUserRole.OPERATOR.value,
            "user-team": OIDCUserRole.USER.value,
            "viewer-team": OIDCUserRole.VIEWER.value,
        },
        is_admin=False,
    )


@pytest.fixture
def admin_user():
    return OIDCAuthManagerUser(
        user_id="test_user",
        name="Test User",
        access_token="this_is_an_access_token",
        refresh_token="this_is_a_refresh_token",
        teams={},
        is_admin=True,
    )


@pytest.mark.skipif(
    not CONF_VARS_PRESENT, reason="Required internal airflow dev package not present."
)
def test_routes(auth_manager):
    assert auth_manager.get_url_login() == "/auth/login"
    assert auth_manager.get_url_logout() == "/auth/logout"


@pytest.mark.skipif(
    not CONF_VARS_PRESENT, reason="Required internal airflow dev package not present."
)
def test_serialization(auth_manager, tmp_user):
    serialized = auth_manager.serialize_user(tmp_user)
    assert serialized["user_id"] == "test_user"
    assert serialized["name"] == "Test User"
    assert serialized["access_token"] == "this_is_an_access_token"
    assert serialized["refresh_token"] == "this_is_a_refresh_token"
    assert serialized["teams"]["operator-team"] == OIDCUserRole.OPERATOR
    assert serialized["teams"]["user-team"] == OIDCUserRole.USER
    assert serialized["teams"]["viewer-team"] == OIDCUserRole.VIEWER
    assert not serialized["admin"]


@pytest.mark.skipif(
    not CONF_VARS_PRESENT, reason="Required internal airflow dev package not present."
)
def test_deserialization(auth_manager):
    serialized = {
        "user_id": "uid",
        "name": "name",
        "access_token": "abc",
        "refresh_token": "def",
        "teams": {"A": OIDCUserRole.ADMIN, "O": OIDCUserRole.OPERATOR},
        "admin": True,
    }
    user = auth_manager.deserialize_user(serialized)
    assert user.get_id() == "uid"
    assert user.get_name() == "name"
    assert user.access_token == "abc"
    assert user.refresh_token == "def"
    assert user.admin
    assert user.get_teams()["A"] == OIDCUserRole.ADMIN.value
    assert user.get_teams()["O"] == OIDCUserRole.OPERATOR.value


@pytest.mark.skipif(
    not CONF_VARS_PRESENT, reason="Required internal airflow dev package not present."
)
def test_client(auth_manager):
    client = auth_manager.get_oidc_client()
    assert client


@pytest.mark.skipif(
    not CONF_VARS_PRESENT, reason="Required internal airflow dev package not present."
)
def test_default_auth(auth_manager, tmp_user, admin_user):
    assert auth_manager._is_authorized_default("GET", tmp_user, "user-team")
    assert auth_manager._is_authorized_default("GET", tmp_user, "operator-team")
    assert auth_manager._is_authorized_default("GET", tmp_user, "viewer-team")

    assert auth_manager._is_authorized_default("POST", tmp_user, "user-team")
    assert auth_manager._is_authorized_default("POST", tmp_user, "operator-team")
    assert not auth_manager._is_authorized_default("POST", tmp_user, "viewer-team")

    assert auth_manager._is_authorized_default("PUT", tmp_user, "user-team")
    assert auth_manager._is_authorized_default("PUT", tmp_user, "operator-team")
    assert not auth_manager._is_authorized_default("PUT", tmp_user, "viewer-team")

    assert auth_manager._is_authorized_default("DELETE", tmp_user, "user-team")
    assert auth_manager._is_authorized_default("DELETE", tmp_user, "operator-team")
    assert not auth_manager._is_authorized_default("DELETE", tmp_user, "viewer-team")

    assert auth_manager._is_authorized_default("GET", admin_user, "operator-team")
    assert auth_manager._is_authorized_default("POST", admin_user, "operator-team")
    assert auth_manager._is_authorized_default("PUT", admin_user, "operator-team")
    assert auth_manager._is_authorized_default("DELETE", admin_user, "operator-team")


@pytest.mark.skipif(
    not CONF_VARS_PRESENT, reason="Required internal airflow dev package not present."
)
def test_auth_functions(auth_manager, tmp_user, admin_user):
    assert auth_manager.is_authorized_team(
        method="GET", user=tmp_user, details=TeamDetails(name="operator-team")
    )
    assert auth_manager.is_authorized_team(
        method="PUT", user=tmp_user, details=TeamDetails(name="operator-team")
    )
    assert auth_manager.is_authorized_team(
        method="POST", user=tmp_user, details=TeamDetails(name="operator-team")
    )
    assert auth_manager.is_authorized_team(
        method="DELETE", user=tmp_user, details=TeamDetails(name="operator-team")
    )

    assert auth_manager.is_authorized_team(
        method="GET", user=tmp_user, details=TeamDetails(name="user-team")
    )
    assert not auth_manager.is_authorized_team(
        method="PUT", user=tmp_user, details=TeamDetails(name="user-team")
    )
    assert not auth_manager.is_authorized_team(
        method="POST", user=tmp_user, details=TeamDetails(name="user-team")
    )
    assert not auth_manager.is_authorized_team(
        method="DELETE", user=tmp_user, details=TeamDetails(name="user-team")
    )

    assert auth_manager.is_authorized_view(
        access_view=AccessView("CLUSTER_ACTIVITY"), user=tmp_user
    )

    assert auth_manager.is_authorized_variable(
        method="GET", user=tmp_user, details=VariableDetails(team_name="operator-team")
    )
    assert not auth_manager.is_authorized_variable(
        method="GET", user=tmp_user, details=VariableDetails(team_name="viewer-team")
    )
    assert not auth_manager.is_authorized_variable(
        method="GET", user=tmp_user, details=VariableDetails(team_name="user-team")
    )

    assert auth_manager.is_authorized_pool(
        method="GET", user=tmp_user, details=PoolDetails(team_name="operator-team")
    )
    assert not auth_manager.is_authorized_pool(
        method="GET", user=tmp_user, details=PoolDetails(team_name="viewer-team")
    )
    assert not auth_manager.is_authorized_pool(
        method="GET", user=tmp_user, details=PoolDetails(team_name="user-team")
    )

    assert auth_manager.is_authorized_connection(
        method="GET", user=tmp_user, details=ConnectionDetails(team_name="operator-team")
    )
    assert auth_manager.is_authorized_connection(
        method="PUT", user=tmp_user, details=ConnectionDetails(team_name="operator-team")
    )
    assert auth_manager.is_authorized_connection(
        method="POST", user=tmp_user, details=ConnectionDetails(team_name="operator-team")
    )
    assert auth_manager.is_authorized_connection(
        method="DELETE", user=tmp_user, details=ConnectionDetails(team_name="operator-team")
    )

    assert auth_manager.is_authorized_connection(
        method="GET", user=tmp_user, details=ConnectionDetails(team_name="user-team")
    )
    assert not auth_manager.is_authorized_connection(
        method="PUT", user=tmp_user, details=ConnectionDetails(team_name="user-team")
    )
    assert not auth_manager.is_authorized_connection(
        method="POST", user=tmp_user, details=ConnectionDetails(team_name="user-team")
    )
    assert not auth_manager.is_authorized_connection(
        method="DELETE", user=tmp_user, details=ConnectionDetails(team_name="user-team")
    )

    assert auth_manager.is_authorized_configuration(method="GET", user=tmp_user)
    assert auth_manager.is_authorized_configuration(method="PUT", user=tmp_user)
    assert auth_manager.is_authorized_configuration(method="POST", user=tmp_user)
    assert auth_manager.is_authorized_configuration(method="DELETE", user=tmp_user)

    assert auth_manager.is_authorized_configuration(method="GET", user=admin_user)
    assert auth_manager.is_authorized_configuration(method="PUT", user=admin_user)
    assert auth_manager.is_authorized_configuration(method="POST", user=admin_user)
    assert auth_manager.is_authorized_configuration(method="DELETE", user=admin_user)
