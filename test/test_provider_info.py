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

from importlib import import_module

from airflow_oidc_provider import get_provider_info
from airflow_oidc_provider.auth_manager.oauth2_auth_manager import OIDCAuthManager


def test_advertised_auth_manager_is_importable():
    class_path = get_provider_info()["auth-managers"][0]
    module_name, class_name = class_path.rsplit(".", 1)

    advertised_class = getattr(import_module(module_name), class_name)

    assert advertised_class is OIDCAuthManager
