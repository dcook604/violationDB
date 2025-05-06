#!/usr/bin/env python3
"""
SQLite to MariaDB Schema Converter

This script:
1. Extracts the table schemas from a SQLite database
2. Converts them to MariaDB-compatible CREATE TABLE statements
3. Handles SQLite-specific features and properly maps data types
4. Generates a SQL file with MariaDB-compatible schemas

Usage:
python sqlite_to_mariadb_schema.py
"""

import sqlite3
import re
import os
from datetime import datetime

# Configuration
SQLITE_DB = 'app.db'
OUTPUT_FILE = 'mariadb_schema.sql'

# Connect to SQLite database
conn = sqlite3.connect(SQLITE_DB)
cursor = conn.cursor()

# Get list of all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
tables = cursor.fetchall()

# SQLite to MariaDB data type mapping
def map_type(sqlite_type):
    sqlite_type = sqlite_type.upper()
    
    # Exact type mappings
    type_map = {
        'INTEGER PRIMARY KEY': 'INT AUTO_INCREMENT PRIMARY KEY',
        'INTEGER NOT NULL PRIMARY KEY': 'INT NOT NULL AUTO_INCREMENT PRIMARY KEY',
        'INTEGER': 'INT',
        'REAL': 'DOUBLE',
        'TEXT': 'TEXT',
        'BLOB': 'BLOB',
        'BOOLEAN': 'TINYINT(1)',
        'TIMESTAMP': 'TIMESTAMP',
        'DATETIME': 'DATETIME',
        'DATE': 'DATE',
        'VARCHAR': 'VARCHAR',  # Will be processed further to include length
    }
    
    # Process VARCHAR with length
    if 'VARCHAR' in sqlite_type:
        length_match = re.search(r'VARCHAR\((\d+)\)', sqlite_type)
        if length_match:
            return f"VARCHAR({length_match.group(1)})"
        return "VARCHAR(255)"  # Default length if not specified
    
    # Handle direct mappings
    for key, value in type_map.items():
        if key in sqlite_type:
            return sqlite_type.replace(key, value)
    
    # Default fallback
    return sqlite_type

# Process each table
output = [
    "-- MariaDB Schema Generated from SQLite",
    f"-- Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    "-- This script creates MariaDB-compatible versions of all tables",
    "",
    "SET FOREIGN_KEY_CHECKS=0;",
    ""
]

# Function to handle default values
def process_default(default_value):
    if default_value is None:
        return ""
    
    # Handle SQLite-specific default expressions
    if default_value == "CURRENT_TIMESTAMP":
        return "DEFAULT CURRENT_TIMESTAMP"
    
    # Convert boolean defaults
    if default_value.lower() in ('0', 'false'):
        return "DEFAULT 0"
    if default_value.lower() in ('1', 'true'):
        return "DEFAULT 1"
    
    # Handle numeric and string defaults
    try:
        float(default_value)  # Check if it's a number
        return f"DEFAULT {default_value}"
    except:
        return f"DEFAULT '{default_value}'"  # It's a string

# Process each table schema
for table in tables:
    table_name = table[0]
    
    # Get schema information for this table
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    
    # Get foreign key information
    cursor.execute(f"PRAGMA foreign_key_list({table_name});")
    foreign_keys = cursor.fetchall()
    
    # Get index information
    cursor.execute(f"PRAGMA index_list({table_name});")
    indices = cursor.fetchall()
    
    # Start building CREATE TABLE statement
    create_table = [f"DROP TABLE IF EXISTS `{table_name}`;", 
                    f"CREATE TABLE `{table_name}` ("]
    
    # Process columns
    column_defs = []
    primary_keys = []
    
    for col in columns:
        col_id, col_name, col_type, not_null, default_val, is_pk = col
        
        # Handle column name with reserved words
        col_name_safe = f"`{col_name}`"
        
        # Convert data type
        mariadb_type = map_type(col_type)
        
        # Build column definition
        col_def = f"  {col_name_safe} {mariadb_type}"
        
        # Add NOT NULL constraint
        if not_null:
            col_def += " NOT NULL"
        
        # Add DEFAULT value
        if default_val is not None:
            col_def += f" {process_default(default_val)}"
        
        # Track primary keys
        if is_pk:
            # Check if it's an auto-increment primary key
            if "INTEGER" in col_type.upper():
                col_def = col_def.replace(mariadb_type, "INT AUTO_INCREMENT")
                primary_keys.append(col_name_safe)
            else:
                primary_keys.append(col_name_safe)
        
        column_defs.append(col_def)
    
    # Add PRIMARY KEY constraint
    if primary_keys:
        if len(primary_keys) == 1 and "AUTO_INCREMENT" in column_defs[columns[0][0]]:
            # Already handled in column definition
            pass
        else:
            column_defs.append(f"  PRIMARY KEY ({', '.join(primary_keys)})")
    
    # Add FOREIGN KEY constraints
    for fk in foreign_keys:
        id, seq, table_ref, from_col, to_col, on_update, on_delete, match = fk
        fk_def = f"  FOREIGN KEY (`{from_col}`) REFERENCES `{table_ref}` (`{to_col}`)"
        
        # Add ON UPDATE clause
        if on_update:
            fk_def += f" ON UPDATE {on_update}"
        
        # Add ON DELETE clause
        if on_delete:
            fk_def += f" ON DELETE {on_delete}"
        
        column_defs.append(fk_def)
    
    # Combine column definitions
    create_table.append(",\n".join(column_defs))
    create_table.append(") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")
    create_table.append("")
    
    # Add the CREATE TABLE statement to the output
    output.extend(create_table)
    
    # Process indices
    for idx in indices:
        # Fix: Unpack only the available columns depending on SQLite version
        idx_name = idx[0]
        unique = idx[1]
        
        # Check if there's an "origin" field (may not exist in older SQLite versions)
        origin = idx[4] if len(idx) > 4 else ""
        
        # Skip auto-created index for primary key
        if origin == "pk":
            continue
        
        # Get index columns
        cursor.execute(f"PRAGMA index_info({idx_name});")
        idx_columns = cursor.fetchall()
        idx_cols = [f"`{col[2]}`" for col in idx_columns]
        
        # Create index statement
        idx_stmt = f"CREATE "
        if unique:
            idx_stmt += "UNIQUE "
        idx_stmt += f"INDEX `{idx_name}` ON `{table_name}` ({', '.join(idx_cols)});"
        
        output.append(idx_stmt)
    
    output.append("")

# Finalize output
output.append("SET FOREIGN_KEY_CHECKS=1;")

# Write to output file
with open(OUTPUT_FILE, 'w') as file:
    file.write('\n'.join(output))

print(f"Conversion complete! MariaDB compatible schema written to {OUTPUT_FILE}")

# Close the database connection
conn.close() 