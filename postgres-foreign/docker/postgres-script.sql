CREATE EXTENSION mysql_fdw;

CREATE SERVER mysql_server
FOREIGN DATA WRAPPER mysql_fdw
OPTIONS (host 'mysql', port '3306');

CREATE USER MAPPING FOR postgres
SERVER mysql_server
OPTIONS (username 'openmetadata_user', password 'openmetadata_password');

CREATE FOREIGN TABLE table_entity (
    id text,
    json JSONB
)
SERVER mysql_server
OPTIONS (dbname 'openmetadata_db', table_name 'table_entity');

CREATE FOREIGN TABLE user_entity (
    id text,
    json JSONB
)
SERVER mysql_server
OPTIONS (dbname 'openmetadata_db', table_name 'table_entity');

COMMIT;
