===========================
Airflow OIDC Integration
===========================

This repo contains a provider package for apache airflow.

It provides an auth_manager that is able to connect to any OIDC compliant Identity Provider, and manages user permissions based on their group memberships, which are mapped to team-roles.

The exact mapping is still work in progress, but it should conform to the roles defined as the current airflow default roles: ``ANONYMOUS``, ``VIEWER``, ``USER``, ``OPERATOR`` and ``ADMIN``.

An example config via variables in a yaml file can look like this::

  AIRFLOW__OAUTH2_AUTH_MANAGER__CLIENT_ID: airflow
  AIRFLOW__OAUTH2_AUTH_MANAGER__CLIENT_SECRET: 'secret configured in the IdP'
  AIRFLOW__OAUTH2_AUTH_MANAGER__SERVER_URL: https://someserver:1234/realms/airflow/.well-known/openid-configuration
  AIRFLOW__OAUTH2_AUTH_MANAGER__SCOPES: "profile email openid roles"
  AIRFLOW__OAUTH2_AUTH_MANAGER__TOKEN_PARSER_CLASS: airflow_oidc_provider.auth_manager.token_parser.SimpleOIDCTokenParser
  AIRFLOW__OAUTH2_AUTH_MANAGER__TOKEN_PARSER_CONFIG: |
  {
      "token_key" : "token_key",
      "admin_group" : "admin",
      "teams" : {
          "Team 1" : {
              "team1:operator" : "operator",
              "team1:user" : "user"
          },
          "Team 2" : {
              "team2:operator" : "operator",
              "team2:viewer" : "viewer",
              "team2:user" : "user"
          }
      }
  }


---------------------
Configuration Options
---------------------

=================================================== ======================================================================= ===========================================================================================
Option name                                         default                                                                 description
=================================================== ======================================================================= ===========================================================================================
AIRFLOW__OAUTH2_AUTH_MANAGER__CLIENT_ID             mandatory                                                               The client id to be used with the IdP.
AIRFLOW__OAUTH2_AUTH_MANAGER__CLIENT_SECRET         mandatory                                                               The client secret to be used with the IdP.
AIRFLOW__OAUTH2_AUTH_MANAGER__SERVER_URL            mandatory                                                               The URL for the OIDC endpoint of the IdP. Often ends in '.well-known/openid-configuration'.
AIRFLOW__OAUTH2_AUTH_MANAGER__SCOPES                profile email openid roles                                              The scopes that need to be requested for the token to contain groups information.
AIRFLOW__OAUTH2_AUTH_MANAGER__TOKEN_PARSER_CLASS    airflow_oidc_provider.auth_manager.token_parser.SimpleOIDCTokenParser   The class that parses the OIDC token for userinformation.
AIRFLOW__OAUTH2_AUTH_MANAGER__TOKEN_PARSER_CONFIG   mandatory for default class, else depends on class                      A config string for the parser class. More details for the default class below.
=================================================== ======================================================================= ===========================================================================================

---------------------
SimpleOIDCTokenParser
---------------------

The SimpleOIDCTokenParser parses the userinfo returned by the IdP for team memberships and access level of the user. To configure it for your specific IdP, and to support slightly off-standard IdPs, it requires some information to parse a token.

The configuration string should be in json format.

+------------+---------------------------------------------------------------------------------------------------------------+
|json key    |  description                                                                                                  |
+============+===============================================================================================================+
|token_key   | The key within the userinfo token, which contains the list of groups the user is a member of                  |
+------------+---------------------------------------------------------------------------------------------------------------+
|admin_group | The name of the group in the userinfo token, which will be matched to airflow ADMIN permissions.              |
+------------+---------------------------------------------------------------------------------------------------------------+
|teams       | This contains nested json objects. On the first Level will be a team name as key, its value will be           |
|            |  a mapping from groups from the userinfo token to the name of the role to be given for this team in airflow.  |===========================
Airflow OIDC Integration
===========================

This repo contains a provider package for apache airflow.

It provides an auth_manager that is able to connect to any OIDC compliant Identity Provider, and manages user permissions based on their group memberships, which are mapped to team-roles.

The exact mapping is still work in progress, but it should conform to the roles defined as the current airflow default roles: ``ANONYMOUS``, ``VIEWER``, ``USER``, ``OPERATOR`` and ``ADMIN``.

An example config via variables in a yaml file can look like this::

  AIRFLOW__OAUTH2_AUTH_MANAGER__CLIENT_ID: airflow
  AIRFLOW__OAUTH2_AUTH_MANAGER__CLIENT_SECRET: 'secret configured in the IdP'
  AIRFLOW__OAUTH2_AUTH_MANAGER__SERVER_URL: https://someserver:1234/realms/airflow/.well-known/openid-configuration
  AIRFLOW__OAUTH2_AUTH_MANAGER__SCOPES: "profile email openid roles"
  AIRFLOW__OAUTH2_AUTH_MANAGER__TOKEN_PARSER_CLASS: airflow_oidc_provider.auth_manager.token_parser.SimpleOIDCTokenParser
  AIRFLOW__OAUTH2_AUTH_MANAGER__TOKEN_PARSER_CONFIG: |
  {
      "token_key" : "token_key",
      "admin_group" : "admin",
      "teams" : {
          "Team 1" : {
              "team1:operator" : "operator",
              "team1:user" : "user"
          },
          "Team 2" : {
              "team2:operator" : "operator",
              "team2:viewer" : "viewer",
              "team2:user" : "user"
          }
      }
  }


---------------------
Configuration Options
---------------------

=================================================== ======================================================================= ===========================================================================================
Option name                                         default                                                                 description
=================================================== ======================================================================= ===========================================================================================
AIRFLOW__OAUTH2_AUTH_MANAGER__CLIENT_ID             mandatory                                                               The client id to be used with the IdP.
AIRFLOW__OAUTH2_AUTH_MANAGER__CLIENT_SECRET         mandatory                                                               The client secret to be used with the IdP.
AIRFLOW__OAUTH2_AUTH_MANAGER__SERVER_URL            mandatory                                                               The URL for the OIDC endpoint of the IdP. Often ends in '.well-known/openid-configuration'.
AIRFLOW__OAUTH2_AUTH_MANAGER__SCOPES                profile email openid roles                                              The scopes that need to be requested for the token to contain groups information.
AIRFLOW__OAUTH2_AUTH_MANAGER__TOKEN_PARSER_CLASS    airflow_oidc_provider.auth_manager.token_parser.SimpleOIDCTokenParser   The class that parses the OIDC token for userinformation.
AIRFLOW__OAUTH2_AUTH_MANAGER__TOKEN_PARSER_CONFIG   mandatory for default class, else depends on class                      A config string for the parser class. More details for the default class below.
=================================================== ======================================================================= ===========================================================================================

---------------------
SimpleOIDCTokenParser
---------------------

The SimpleOIDCTokenParser parses the userinfo returned by the IdP for team memberships and access level of the user. To configure it for your specific IdP, and to support slightly off-standard IdPs, it requires some information to parse a token.

The configuration string should be in json format.

+------------+---------------------------------------------------------------------------------------------------------------+
|json key    |  description                                                                                                  |
+============+===============================================================================================================+
|token_key   | The key within the userinfo token, which contains the list of groups the user is a member of                  |
+------------+---------------------------------------------------------------------------------------------------------------+
|admin_group | The name of the group in the userinfo token, which will be matched to airflow ADMIN permissions.              |
+------------+---------------------------------------------------------------------------------------------------------------+
|teams       | This contains nested json objects. On the first Level will be a team name as key, its value will be           |
|            | a mapping from groups from the userinfo token to the name of the role to be given for this team in airflow.   |
+------------+---------------------------------------------------------------------------------------------------------------+
