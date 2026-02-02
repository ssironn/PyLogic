-- PyLogic Database Initialization Script
-- This script runs automatically when the MySQL container starts for the first time

-- Set character set
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- Grant privileges to the application user
GRANT ALL PRIVILEGES ON pylogic.* TO 'pylogic'@'%';
FLUSH PRIVILEGES;

-- Note: Tables are created by Flask-SQLAlchemy's db.create_all()
-- This script only sets up the database and user permissions
