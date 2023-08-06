/*
2013.5.12 CKS
Lists all table sizes.
*/
DROP VIEW IF EXISTS database_size_table CASCADE;
CREATE OR REPLACE VIEW database_size_table
AS
SELECT  CONCAT(CAST(schemaname AS VARCHAR), '-', CAST(tablename AS VARCHAR)) AS id,
        schemaname AS schema_name,
        tablename AS table_name,
        tableowner AS table_owner,
        pg_total_relation_size(schemaname || '.' || tablename) AS size_in_bytes
FROM    pg_tables;