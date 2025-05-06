# SQLite to MariaDB Migration Guide

This document outlines the process of migrating the Violation Management System's database from SQLite to MariaDB.

## Overview

The migration includes:
1. Converting SQLite table schemas to MariaDB-compatible formats
2. Migrating data with proper type handling
3. Updating application configuration to use MariaDB
4. Setting up the MariaDB database

## Prerequisites

- Python 3.6+
- MariaDB/MySQL server (tested with MariaDB 10.5+)
- Python packages: `pymysql`, `mysqlclient`

## Migration Scripts

Three main scripts handle the migration process:

### 1. `sqlite_to_mariadb_schema.py`
Converts SQLite schemas to MariaDB-compatible CREATE TABLE statements.

- Maps SQLite data types to MariaDB equivalents
- Handles primary keys, foreign keys, and indices
- Generates proper SQL syntax compatible with MariaDB
- Creates a `mariadb_schema.sql` file

**Key features:**
- Proper handling of auto-increment fields
- Translation of SQLite-specific constraints
- Character set and collation setup (utf8mb4)
- Foreign key relationship preservation

### 2. `sqlite_to_mariadb_data.py`
Extracts data from SQLite and generates MariaDB-compatible INSERT statements.

- Handles data type conversions
- Escapes special characters
- Formats dates and times correctly
- Generates a `mariadb_data.sql` file

**Key features:**
- Batch inserts for better performance
- Proper escaping of string values
- JSON data handling
- Transaction-based imports

### 3. `update_db_config.py`
Updates application configuration to use MariaDB instead of SQLite.

- Modifies `app/config.py` to use MariaDB connection string
- Updates `alembic.ini` for database migrations
- Ensures required dependencies are installed
- Creates backups of modified files

## Migration Process

### Step 1: Run the Schema Conversion
```bash
python sqlite_to_mariadb_schema.py
```
This generates a `mariadb_schema.sql` file with MariaDB-compatible CREATE TABLE statements.

### Step 2: Run the Data Migration
```bash
python sqlite_to_mariadb_data.py
```
This generates a `mariadb_data.sql` file with INSERT statements for all data.

### Step 3: Update Application Configuration
```bash
python update_db_config.py
```
This updates configuration files to use MariaDB and creates backups.

### Step 4: Set Up MariaDB Database
Create the database and user:
```sql
CREATE DATABASE violationdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'violation'@'localhost' IDENTIFIED BY 'n2hm13i';
GRANT ALL PRIVILEGES ON violationdb.* TO 'violation'@'localhost';
FLUSH PRIVILEGES;
```

### Step 5: Import Schema and Data
```bash
mysql -u violation -p violationdb < mariadb_schema.sql
mysql -u violation -p violationdb < mariadb_data.sql
```

### Step 6: Update Alembic Migration Head
```bash
flask db stamp head
```

## Data Type Mappings

| SQLite Type | MariaDB Type |
|-------------|--------------|
| INTEGER PRIMARY KEY | INT AUTO_INCREMENT PRIMARY KEY |
| INTEGER | INT |
| REAL | DOUBLE |
| TEXT | TEXT |
| BLOB | BLOB |
| BOOLEAN | TINYINT(1) |
| TIMESTAMP | TIMESTAMP |
| DATETIME | DATETIME |
| DATE | DATE |
| VARCHAR(n) | VARCHAR(n) |

## Known Issues and Limitations

1. SQLite allows more flexible data types - some data might need manual verification
2. JSON data stored as TEXT in SQLite is preserved but not converted to MariaDB's JSON type
3. CURRENT_TIMESTAMP default values are mapped but behavior may differ slightly
4. Some SQLite indices might require manual optimization in MariaDB
5. Make sure to verify all foreign key relationships after migration

## Troubleshooting

### Error: "Unknown collation: 'utf8mb4_unicode_ci'"
Older MariaDB/MySQL versions might not support utf8mb4_unicode_ci. Try using utf8mb4_general_ci instead.

### Error: "Foreign key constraint fails"
Import may fail if data is imported in the wrong order. Try:
1. Disable foreign key checks before import (already in scripts)
2. Check data integrity in SQLite before migration

### Error: "Incorrect integer value: '' for column..."
Some INTEGER columns might contain empty strings in SQLite. They are converted to NULL in MariaDB.

## Rollback Procedure

The migration scripts create backups of modified files. To roll back:
1. Restore `app/config.py.bak` to `app/config.py`
2. Restore `alembic.ini.bak` to `alembic.ini`
3. Continue using the SQLite database

## Verification Steps

After migration:
1. Test application functionality
2. Verify all data has been correctly migrated
3. Check database performance
4. Ensure all foreign key constraints are intact 