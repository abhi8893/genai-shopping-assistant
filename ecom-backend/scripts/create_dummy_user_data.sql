-- Insert users
DELETE FROM "user";

INSERT INTO "user" (id, first_name, last_name, role, created_at) VALUES
(1, 'John', 'Doe', 'user', CURRENT_TIMESTAMP),
(2, 'Jane', 'Smith', 'admin', CURRENT_TIMESTAMP),
(3, 'Bob', 'Johnson', 'user', CURRENT_TIMESTAMP),
(4, 'Alice', 'Williams', 'user', CURRENT_TIMESTAMP);