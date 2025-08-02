-- Add password_hash column to existing users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);

-- Update the column to be NOT NULL after adding it
-- First, set a default value for existing rows (if any)
UPDATE users SET password_hash = 'temp_hash' WHERE password_hash IS NULL;

-- Then make it NOT NULL
ALTER TABLE users ALTER COLUMN password_hash SET NOT NULL;

-- Add index for better performance
CREATE INDEX IF NOT EXISTS idx_users_password_hash ON users(password_hash);
