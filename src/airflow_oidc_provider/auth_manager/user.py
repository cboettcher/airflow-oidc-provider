from enum import IntEnum

from airflow.api_fastapi.auth.managers.models.base_user import BaseUser


class OIDCUserRole(IntEnum):
    ANONYMOUS = 0
    VIEWER = 1
    USER = 2
    OPERATOR = 3
    ADMIN = 4


class OIDCAuthManagerUser(BaseUser):
    """User model for Users managed by the oauth2 auth manager."""

    def __init__(
        self,
        user_id: str,
        name: str,
        access_token: str,
        refresh_token: str | None,
        teams: dict[str, int] = {},
        is_admin: bool = False,
    ) -> None:
        self.user_id = user_id
        self.name = name
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.teams: dict[str, OIDCUserRole] = {}
        self.admin = is_admin
        for team in teams:
            self.teams[team] = OIDCUserRole(value=teams[team])

    def get_id(self) -> str:
        return self.user_id

    def get_name(self) -> str:
        return self.name

    def add_team(self, team: str, role: int):
        self.teams[team] = OIDCUserRole(value=role)

    def get_role(self, team: str) -> str:
        return self.teams[team].name

    def get_role_value(self, team: str) -> int:
        return self.teams[team].value

    def get_teams(self) -> dict[str, OIDCUserRole]:
        return self.teams

    def _is_at_least(self, role: OIDCUserRole, team: str | None = None) -> bool:
        if self.admin:
            return True
        if team is not None:
            return self.teams.get(team, OIDCUserRole.ANONYMOUS).value >= role.value
        # if no team is given, we check if the user has the required role for at least one team
        for team_name in self.teams.keys():
            if self.teams[team_name].value >= role.value:
                return True
        return False

    def is_viewer(self, team: str | None = None) -> bool:
        return self._is_at_least(OIDCUserRole.VIEWER, team)

    def is_user(self, team: str | None = None) -> bool:
        return self._is_at_least(OIDCUserRole.USER, team)

    def is_operator(self, team: str | None = None) -> bool:
        return self._is_at_least(OIDCUserRole.OPERATOR, team)

    def is_admin(self, team: str | None = None) -> bool:
        return self.admin or self._is_at_least(OIDCUserRole.ADMIN, team)
