CREATE DATABASE IF NOT EXISTS ce_test_slurmdb;
CREATE USER 'ce-test-slurm'@'localhost';
GRANT USAGE ON *.* TO 'ce-test-slurm'@'localhost';
GRANT ALL PRIVILEGES ON ce_test_slurmdb.* TO 'ce-test-slurm'@'localhost' identified BY 'ce-test';
FLUSH PRIVILEGES;
