#!/usr/bin/env python3
"""
Update Database Configuration Script

This script:
1. Modifies the application configuration to use MariaDB instead of SQLite
2. Updates the database connection URL in config.py
3. Updates alembic.ini for migrations
4. Ensures all necessary dependencies are installed

Usage:
python update_db_config.py
"""

import os
import re
import sys
import subprocess
import shutil

# Configuration
MARIADB_CONFIG = {
    'host': 'localhost',
    'port': '3309',
    'database': 'violationdb',
    'user': 'violation',
    'password': 'n2hm13i'
}

DB_URL = f"mysql+pymysql://{MARIADB_CONFIG['user']}:{MARIADB_CONFIG['password']}@{MARIADB_CONFIG['host']}:{MARIADB_CONFIG['port']}/{MARIADB_CONFIG['database']}"

# File paths
APP_CONFIG_FILE = 'app/config.py'
ALEMBIC_CONFIG_FILE = 'alembic.ini'
REQUIREMENTS_FILE = 'requirements.txt'

# Backup function
def backup_file(file_path):
    """Create a backup of a file with .bak extension"""
    backup_path = f"{file_path}.bak"
    print(f"Creating backup of {file_path} to {backup_path}")
    shutil.copy2(file_path, backup_path)

# Update app/config.py
def update_app_config():
    """Update the database URL in app/config.py"""
    if not os.path.exists(APP_CONFIG_FILE):
        print(f"Error: {APP_CONFIG_FILE} not found!")
        return False
    
    backup_file(APP_CONFIG_FILE)
    
    with open(APP_CONFIG_FILE, 'r') as file:
        content = file.read()
    
    # Find and replace the SQLite connection string
    sqlite_pattern = r"'sqlite:///'\s*\+\s*os\.path\.join\(BASE_DIR,\s*'app\.db'\)"
    mariadb_replacement = f"'{DB_URL}'"
    
    # Check if we need to replace the default SQLite connection string
    if re.search(sqlite_pattern, content):
        content = re.sub(sqlite_pattern, mariadb_replacement, content)
        print(f"Updated default SQLAlchemy database URI in {APP_CONFIG_FILE}")
    
    # Write the updated content back to the file
    with open(APP_CONFIG_FILE, 'w') as file:
        file.write(content)
    
    return True

# Update alembic.ini
def update_alembic_config():
    """Update the database URL in alembic.ini"""
    if not os.path.exists(ALEMBIC_CONFIG_FILE):
        print(f"Error: {ALEMBIC_CONFIG_FILE} not found!")
        return False
    
    backup_file(ALEMBIC_CONFIG_FILE)
    
    with open(ALEMBIC_CONFIG_FILE, 'r') as file:
        content = file.read()
    
    # Find and replace the sqlalchemy.url line
    url_pattern = r"sqlalchemy\.url\s*=\s*[^\n]+"
    url_replacement = f"sqlalchemy.url = {DB_URL}"
    
    if re.search(url_pattern, content):
        content = re.sub(url_pattern, url_replacement, content)
        print(f"Updated sqlalchemy.url in {ALEMBIC_CONFIG_FILE}")
    else:
        # If not found, add it
        content += f"\n# Added by migration script\nsqlalchemy.url = {DB_URL}\n"
        print(f"Added sqlalchemy.url to {ALEMBIC_CONFIG_FILE}")
    
    # Write the updated content back to the file
    with open(ALEMBIC_CONFIG_FILE, 'w') as file:
        file.write(content)
    
    return True

# Update requirements.txt
def update_requirements():
    """Ensure MySQL/MariaDB dependencies are in requirements.txt"""
    if not os.path.exists(REQUIREMENTS_FILE):
        print(f"Error: {REQUIREMENTS_FILE} not found!")
        return False
    
    backup_file(REQUIREMENTS_FILE)
    
    with open(REQUIREMENTS_FILE, 'r') as file:
        content = file.readlines()
    
    # Check if dependencies are already in requirements.txt
    dependencies = {
        'pymysql': 'pymysql>=1.0.2',
        'mysqlclient': 'mysqlclient>=2.1.0'
    }
    
    existing_deps = {line.split('==')[0].split('>=')[0].strip().lower() for line in content}
    
    with open(REQUIREMENTS_FILE, 'a') as file:
        for dep_name, dep_line in dependencies.items():
            if dep_name.lower() not in existing_deps:
                file.write(f"{dep_line}\n")
                print(f"Added {dep_name} to {REQUIREMENTS_FILE}")
    
    return True

# Install dependencies
def install_dependencies():
    """Install required Python packages"""
    print("Installing required Python packages...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pymysql', 'mysqlclient'], check=True)
        print("Successfully installed dependencies")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False

# Main function
def main():
    print("Starting database configuration update...")
    
    # Update configuration files
    app_config_updated = update_app_config()
    alembic_config_updated = update_alembic_config()
    requirements_updated = update_requirements()
    
    # Install dependencies
    dependencies_installed = install_dependencies()
    
    # Summary
    print("\nUpdate Summary:")
    print(f"- App config updated: {'✓' if app_config_updated else '✗'}")
    print(f"- Alembic config updated: {'✓' if alembic_config_updated else '✗'}")
    print(f"- Requirements updated: {'✓' if requirements_updated else '✗'}")
    print(f"- Dependencies installed: {'✓' if dependencies_installed else '✗'}")
    
    if app_config_updated and alembic_config_updated:
        print("\nConfiguration update completed successfully!")
        print(f"\nMariaDB Connection URL: {DB_URL}")
        print("\nNext steps:")
        print("1. Create MariaDB database and user:")
        print("   ```")
        print("   CREATE DATABASE violationdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        print("   CREATE USER 'violation'@'localhost' IDENTIFIED BY 'n2hm13i';")
        print("   GRANT ALL PRIVILEGES ON violationdb.* TO 'violation'@'localhost';")
        print("   FLUSH PRIVILEGES;")
        print("   ```")
        print("2. Run the schema creation script:")
        print("   ```")
        print("   mysql -u violation -p violationdb < mariadb_schema.sql")
        print("   ```")
        print("3. Import the data:")
        print("   ```")
        print("   mysql -u violation -p violationdb < mariadb_data.sql")
        print("   ```")
        print("4. Update migrations head:")
        print("   ```")
        print("   flask db stamp head")
        print("   ```")
    else:
        print("\nConfiguration update failed. Please check the errors above.")

if __name__ == "__main__":
    main() 