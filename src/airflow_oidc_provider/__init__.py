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


def get_provider_info():
    return {
        "package-name": "airflow-oidc-provider",
        "name": "Oauth2",
        "description": "Apache Airflow OIDC provider containing an authManager.",
        "auth-managers": [
            "airflow_oauth2_provider.auth_manager.oauth2_auth_manager.OIDCAuthManager"
        ],
        "cli": [],
        "config": {
            "oauth2_auth_manager": {
                "description": "This section contains settings for the OIDC auth manager integration.",
                "options": {
                    "client_id": {
                        "description": "Client ID configured in the IdP to integrate with Airflow.\nThis client must follow the standard OpenID Connect authentication flow.\n",
                        "type": "string",
                        "version_added": "0.0.1",
                        "example": None,
                        "default": None,
                    },
                    "scopes": {
                        "description": "Scopes to be appended to the oauth configuration.\n",
                        "type": "string",
                        "sensitive": True,
                        "version_added": "0.0.1",
                        "example": None,
                        "default": "openid email profile",
                    },
                    "client_secret": {
                        "description": "Secret associated to the client configured in the IdP to integrate with Airflow.\n",
                        "type": "string",
                        "sensitive": True,
                        "version_added": "0.0.1",
                        "example": None,
                        "default": None,
                    },
                    "server_url": {
                        "description": "The OIDC endpoint of the IdP.",
                        "type": "string",
                        "version_added": "0.0.1",
                        "example": None,
                        "default": None,
                    },
                    "requests_pool_size": {
                        "description": "Size of the connection pool used by the OIDC auth manager.\nThis setting improves performance when multiple requests are made to the IdP.\n",
                        "type": "integer",
                        "version_added": "0.0.1",
                        "example": "10",
                        "default": "10",
                    },
                    "requests_retries": {
                        "description": "Number of retries for failed requests made by the OIDC auth manager.\nThis setting helps to handle transient network issues.\n",
                        "type": "integer",
                        "version_added": "0.0.1",
                        "example": "3",
                        "default": "3",
                    },
                    "token_parser_class": {
                        "description": "The full classpath to be used as a parser of the token.\n",
                        "type": "string",
                        "version_added": "0.0.1",
                        "example": "airflow_oidc_provider.auth_manager.token_parser.SimpleOIDCTokenParser",
                        "default": "airflow_oidc_provider.auth_manager.token_parser.SimpleOIDCTokenParser",
                    },
                    "token_parser_config": {
                        "description": "A config String for the token parser class.\nStructure depends on the configured class, for the SimpleOIDCTokenParse it is a json string like the example.",
                        "type": "string",
                        "version_added": "0.0.1",
                        "example": """
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
        }""",
                        "default": None,
                    },
                },
            }
        },
    }
