CONF_SECTION_NAME = "oauth2_auth_manager"
CONF_CLIENT_ID_KEY = "client_id"
CONF_CLIENT_SECRET_KEY = "client_secret"
CONF_SERVER_URL_KEY = "server_url"
CONF_SCOPES = "scopes"
CONF_REQUESTS_POOL_SIZE_KEY = "requests_pool_size"
CONF_REQUESTS_RETRIES_KEY = "requests_retries"

CONF_TOKEN_PARSER_CONFIG = "token_parser_config"
CONF_TOKEN_PARSER_CLASS_DEFAULT = (
    "airflow_oidc_provider.auth_manager.token_parser.SimpleOIDCTokenParser"
)

CONF_TOKEN_PARSER_CLASS = "token_parser_class"

CONF_SCOPES_DEFAULT = "openid email profile"
