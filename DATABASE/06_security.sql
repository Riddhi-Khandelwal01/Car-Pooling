
USE campusride;

-- Create application user
CREATE USER IF NOT EXISTS
'campus_app'@'localhost'
IDENTIFIED BY 'CHANGE_THIS_PASSWORD';

-- Give required permissions
GRANT SELECT, INSERT, UPDATE, EXECUTE
ON campusride.*
TO 'campus_app'@'localhost';

-- Display permissions
SHOW GRANTS FOR 'campus_app'@'localhost';

-- Temporarily revoke UPDATE permission
REVOKE UPDATE
ON campusride.*
FROM 'campus_app'@'localhost';

-- Verify permissions
SHOW GRANTS FOR 'campus_app'@'localhost';

-- Restore UPDATE permission for GUI functionality
GRANT UPDATE
ON campusride.*
TO 'campus_app'@'localhost';

-- Final permission verification
SHOW GRANTS FOR 'campus_app'@'localhost';
