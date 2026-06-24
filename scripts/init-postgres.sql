-- 在 john-server 上执行一次，创建 ReadHub 专用库和用户。
-- docker exec -i john-postgresql psql -U appuser -d appdb < scripts/init-postgres.sql

CREATE USER readhub WITH PASSWORD 'readhub-123';
CREATE DATABASE readhub OWNER readhub;
GRANT ALL PRIVILEGES ON DATABASE readhub TO readhub;
