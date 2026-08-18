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

import pytest
from starlette.requests import Request

from airflow_oidc_provider.auth_manager.routes import login as login_routes


def _request(scheme):
    return Request(
        {
            "type": "http",
            "method": "GET",
            "scheme": scheme,
            "path": "/auth/login_callback",
            "raw_path": b"/auth/login_callback",
            "query_string": b"",
            "headers": [(b"host", b"airflow.example.org")],
            "server": ("airflow.example.org", 443),
        }
    )


@pytest.mark.parametrize(
    ("scheme", "ssl_cert", "expected"),
    [
        ("https", "", True),
        ("http", "/cert.pem", True),
        ("http", "", False),
    ],
)
def test_cookie_secure_policy(monkeypatch, scheme, ssl_cert, expected):
    def fake_get(section, key, fallback=None):
        assert (section, key) == ("api", "ssl_cert")
        return ssl_cert

    monkeypatch.setattr(login_routes.conf, "get", fake_get)

    assert login_routes._is_cookie_secure(_request(scheme)) is expected
