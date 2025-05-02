-- Add account lockout and Argon2 password hashing support for SQLite

-- SQLite doesn't support ALTER COLUMN directly, so we'll use a more complex approach

-- Step 1: Create a temporary table with the new schema
CREATE TABLE users_new (
    id INTEGER PRIMARY KEY,
    email VARCHAR(120) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT 0,
    is_active BOOLEAN DEFAULT 0,
    role VARCHAR(50) DEFAULT 'user',
    temp_password VARCHAR(255),
    temp_password_expiry DATETIME,
    created_at DATETIME,
    last_login DATETIME,
    failed_login_attempts INTEGER DEFAULT 0,
    last_failed_login DATETIME,
    account_locked_until DATETIME,
    password_algorithm VARCHAR(20) DEFAULT 'werkzeug'
);

-- Step 2: Copy data from the old table to the new one
INSERT INTO users_new (id, email, password_hash, is_admin, is_active, role, temp_password, temp_password_expiry, created_at, last_login)
SELECT id, email, password_hash, is_admin, is_active, role, temp_password, temp_password_expiry, created_at, last_login FROM users;

-- Step 3: Drop the old table
DROP TABLE users;

-- Step 4: Rename the new table to the original name
ALTER TABLE users_new RENAME TO users;

-- Step 5: Set default values for new columns
UPDATE users SET failed_login_attempts = 0 WHERE failed_login_attempts IS NULL;
UPDATE users SET password_algorithm = 'werkzeug' WHERE password_algorithm IS NULL; 