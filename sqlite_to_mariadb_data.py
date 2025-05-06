#!/usr/bin/env python3
"""
SQLite to MariaDB Data Converter

This script:
1. Extracts data from a SQLite database
2. Converts the data to MariaDB-compatible INSERT statements
3. Handles data type conversions between SQLite and MariaDB
4. Generates a SQL file with data migration statements

Usage:
python sqlite_to_mariadb_data.py
"""

import sqlite3
import re
import os
import json
from datetime import datetime

# Configuration
SQLITE_DB = 'app.db'
OUTPUT_FILE = 'mariadb_data.sql'
BATCH_SIZE = 100  # Number of rows per INSERT statement

# Connect to SQLite database
conn = sqlite3.connect(SQLITE_DB)
# Enable column name access
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get list of all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
tables = cursor.fetchall()

# Start output
output = [
    "-- MariaDB Data Migration from SQLite",
    f"-- Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    "-- This script migrates data from SQLite to MariaDB",
    "",
    "SET FOREIGN_KEY_CHECKS=0;",
    "SET UNIQUE_CHECKS=0;",
    "SET AUTOCOMMIT=0;",
    ""
]

def escape_value(value, column_type):
    """Escape and format a value based on its column type for MariaDB"""
    if value is None:
        return "NULL"
    
    column_type = column_type.upper()
    
    # Boolean values
    if 'BOOLEAN' in column_type or 'TINYINT' in column_type:
        if isinstance(value, bool):
            return "1" if value else "0"
        if isinstance(value, int):
            return "1" if value else "0"
        if isinstance(value, str):
            return "1" if value.lower() in ('true', 't', 'yes', 'y', '1') else "0"
        return "0"  # Default
    
    # String/text types
    if 'VARCHAR' in column_type or 'TEXT' in column_type or 'CHAR' in column_type:
        # Handle potential JSON data stored as text
        if isinstance(value, str) and (value.startswith('{') or value.startswith('[')):
            try:
                # Try to parse as JSON to ensure it's properly formatted
                json.loads(value)
                # Properly escape quotes and backslashes
                escaped = value.replace('\\', '\\\\').replace("'", "\\'")
                return f"'{escaped}'"
            except:
                # Not valid JSON, treat as regular string
                pass
        
        # Regular string value
        if isinstance(value, str):
            escaped = value.replace('\\', '\\\\').replace("'", "\\'")
            return f"'{escaped}'"
        return f"'{value}'"
    
    # Date/time types
    if 'DATETIME' in column_type or 'TIMESTAMP' in column_type:
        # SQLite stores dates in various formats, standardize
        if isinstance(value, str):
            try:
                # Try to parse with different formats
                formats = [
                    '%Y-%m-%d %H:%M:%S',
                    '%Y-%m-%d %H:%M:%S.%f',
                    '%Y-%m-%dT%H:%M:%S',
                    '%Y-%m-%dT%H:%M:%S.%f'
                ]
                for fmt in formats:
                    try:
                        dt = datetime.strptime(value, fmt)
                        return f"'{dt.strftime('%Y-%m-%d %H:%M:%S')}'"
                    except:
                        continue
            except:
                pass
            
            # If we couldn't parse it, just return as-is
            return f"'{value}'"
        
        # If it's already a datetime object
        if isinstance(value, datetime):
            return f"'{value.strftime('%Y-%m-%d %H:%M:%S')}'"
        
        return f"'{value}'"
    
    # Date type
    if 'DATE' in column_type:
        return f"'{value}'"
    
    # Numeric types
    return str(value)

# Process each table
for table_item in tables:
    table_name = table_item[0]
    print(f"Processing table: {table_name}")
    
    # Get table structure
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    column_types = {col[1]: col[2] for col in columns}
    
    # Get total count
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    total_rows = cursor.fetchone()[0]
    
    if total_rows == 0:
        print(f"  Table {table_name} is empty. Skipping.")
        continue
    
    # Disable unique keys and auto increment
    output.append(f"-- Table: {table_name}")
    output.append(f"-- Total rows: {total_rows}")
    output.append(f"TRUNCATE TABLE `{table_name}`;")
    
    # Process data in batches
    for offset in range(0, total_rows, BATCH_SIZE):
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {BATCH_SIZE} OFFSET {offset};")
        rows = cursor.fetchall()
        
        if not rows:
            break
        
        # Start the INSERT statement
        if len(rows) == 1:
            # Single row insert
            insert_stmt = f"INSERT INTO `{table_name}` (`{'`, `'.join(column_names)}`) VALUES\n"
        else:
            # Multi-row insert
            insert_stmt = f"INSERT INTO `{table_name}` (`{'`, `'.join(column_names)}`) VALUES\n"
        
        value_strings = []
        
        # Process each row
        for row in rows:
            values = []
            for col_name in column_names:
                values.append(escape_value(row[col_name], column_types[col_name]))
            
            value_strings.append(f"({', '.join(values)})")
        
        # Combine all rows
        insert_stmt += ",\n".join(value_strings) + ";"
        output.append(insert_stmt)
    
    # Add a separator between tables
    output.append("")

# Finalize output
output.append("COMMIT;")
output.append("SET UNIQUE_CHECKS=1;")
output.append("SET FOREIGN_KEY_CHECKS=1;")

# Write to output file
with open(OUTPUT_FILE, 'w') as file:
    file.write('\n'.join(output))

print(f"Data conversion complete! MariaDB compatible INSERT statements written to {OUTPUT_FILE}")

# Close the database connection
conn.close() 