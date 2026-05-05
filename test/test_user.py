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

from airflow_oidc_provider.auth_manager.user import OIDCAuthManagerUser
from airflow_oidc_provider.auth_manager.user import OIDCUserRole

test_userid = "testuser"
test_username = "Test User"
test_token = "piufgpisejhfvowehgflasehgbvlasefgvlsjkdv"
test_teams = {"A-Team": OIDCUserRole.OPERATOR.value, "B-Team": OIDCUserRole.USER.value}
more_teams = {
    "C-Team": OIDCUserRole.VIEWER.value,
    "D-Team": OIDCUserRole.ANONYMOUS.value,
    "E-Team": OIDCUserRole.ADMIN.value,
}


def test_enum_from_value():
    assert OIDCUserRole(value=0) == OIDCUserRole.ANONYMOUS
    assert OIDCUserRole(value=1) == OIDCUserRole.VIEWER
    assert OIDCUserRole(value=2) == OIDCUserRole.USER
    assert OIDCUserRole(value=3) == OIDCUserRole.OPERATOR
    assert OIDCUserRole(value=4) == OIDCUserRole.ADMIN


def test_enum_from_name():
    assert OIDCUserRole["ADMIN"] == OIDCUserRole.ADMIN
    assert OIDCUserRole["user".upper()] == OIDCUserRole.USER


def test_init():
    user = OIDCAuthManagerUser(test_userid, test_username, test_teams)
    assert user
    assert user.user_id == test_userid
    assert user.name == test_username
    assert user.teams["A-Team"] == OIDCUserRole.OPERATOR.value
    assert user.admin is False


def test_add_team():
    user = OIDCAuthManagerUser(test_userid, test_username, test_teams)
    assert user.teams.get("C-Team") is None
    user.add_team("C-Team", OIDCUserRole.VIEWER)
    assert user.teams.get("C-Team") == OIDCUserRole.VIEWER


def test_get_role():
    testuser = OIDCAuthManagerUser(test_userid, test_username, test_teams)
    assert testuser.get_role("A-Team") == OIDCUserRole.OPERATOR.name
    assert testuser.get_role_value("A-Team") == OIDCUserRole.OPERATOR.value


def test_is_at_least():
    tmp_teams = test_teams
    testuser = OIDCAuthManagerUser(test_userid, test_username, tmp_teams)
    testuser2 = OIDCAuthManagerUser(test_userid, test_username, more_teams)
    assert testuser.is_viewer("A-Team")
    assert testuser.is_user("A-Team")
    assert testuser.is_operator("A-Team")

    assert testuser.is_viewer("B-Team")
    assert testuser.is_user("B-Team")
    assert testuser.is_operator("B-Team") is False

    assert testuser2.is_viewer("C-Team")
    assert testuser2.is_user("C-Team") is False
    assert testuser2.is_operator("C-Team") is False
    assert testuser2.is_viewer("A-Team") is False

    assert testuser.is_admin() is False
    assert testuser2.is_admin()
    assert testuser2.is_admin("A-team") is False
