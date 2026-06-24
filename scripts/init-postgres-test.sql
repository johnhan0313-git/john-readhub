-- 测试库（与 english-study-test 等命名一致）
-- docker exec -i john-postgresql psql -U appuser -d appdb < scripts/init-postgres-test.sql

CREATE DATABASE "readhub-test" OWNER readhub;
GRANT ALL PRIVILEGES ON DATABASE "readhub-test" TO readhub;
