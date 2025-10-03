-- Add test user to existing database
-- Run this with: docker-compose exec postgres psql -U postgres -d edunote -f /docker-entrypoint-initdb.d/add_test_user.sql

-- Insert default test user
INSERT INTO app_user (id, email, display_name, password) 
VALUES (
    '00000000-0000-0000-0000-000000000001'::uuid,
    'demo@user.com',
    'Test User',
    'password123'
) ON CONFLICT (email) DO NOTHING;

-- Verify the user was added
SELECT * FROM app_user WHERE email = 'demo@user.com';
