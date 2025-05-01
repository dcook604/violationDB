-- Add account lockout and Argon2 password hashing support

-- Update the length of password_hash and temp_password columns
ALTER TABLE users MODIFY COLUMN password_hash VARCHAR(255) NOT NULL;
ALTER TABLE users MODIFY COLUMN temp_password VARCHAR(255) NULL;

-- Add new columns for account lockout and password algorithm
ALTER TABLE users ADD COLUMN failed_login_attempts INT DEFAULT 0;
ALTER TABLE users ADD COLUMN last_failed_login DATETIME NULL;
ALTER TABLE users ADD COLUMN account_locked_until DATETIME NULL;
ALTER TABLE users ADD COLUMN password_algorithm VARCHAR(20) DEFAULT 'werkzeug';

-- Set default values for new columns
UPDATE users SET failed_login_attempts = 0;
UPDATE users SET password_algorithm = 'werkzeug'; 