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
from starlette.middleware.sessions import SessionMiddleware

from airflow_oidc_provider.auth_manager import oauth2_auth_manager as auth_manager_module
from airflow_oidc_provider.auth_manager.oauth2_auth_manager import OIDCAuthManager


def _get_session_middleware_options(app):
    middleware = next(item for item in app.user_middleware if item.cls is SessionMiddleware)
    return middleware.kwargs


def _patch_api_config(monkeypatch, **values):
    def fake_get(section, key, fallback=None):
        assert section == "api"
        return values.get(key, fallback)

    monkeypatch.setattr(auth_manager_module.conf, "get", fake_get)


def test_session_middleware_uses_airflow_api_secret(monkeypatch):
    _patch_api_config(monkeypatch, secret_key="configured-secret")

    auth_manager = OIDCAuthManager.__new__(OIDCAuthManager)

    assert _get_session_middleware_options(auth_manager.get_fastapi_app())["secret_key"] == (
        "configured-secret"
    )


@pytest.mark.parametrize(
    ("base_url", "ssl_cert", "expected_https_only"),
    [
        ("https://airflow.example.org", "", True),
        ("http://airflow.example.org", "/cert.pem", True),
        ("http://airflow.example.org", "", False),
    ],
)
def test_session_cookie_secure_policy(monkeypatch, base_url, ssl_cert, expected_https_only):
    _patch_api_config(
        monkeypatch,
        base_url=base_url,
        secret_key="configured-secret",
        ssl_cert=ssl_cert,
    )

    auth_manager = OIDCAuthManager.__new__(OIDCAuthManager)
    options = _get_session_middleware_options(auth_manager.get_fastapi_app())

    assert options["https_only"] is expected_https_only
