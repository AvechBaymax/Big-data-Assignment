-- Add this to scripts/init_db.sql
CREATE DATABASE metastore;
CREATE USER hive WITH PASSWORD 'hive123';
GRANT ALL PRIVILEGES ON DATABASE metastore TO hive;