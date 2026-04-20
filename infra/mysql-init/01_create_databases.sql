CREATE DATABASE IF NOT EXISTS ecommerce_auth CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS ecommerce_users CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS ecommerce_cart CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS ecommerce_orders CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS ecommerce_payments CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

GRANT ALL PRIVILEGES ON ecommerce_auth.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON ecommerce_users.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON ecommerce_cart.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON ecommerce_orders.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON ecommerce_payments.* TO 'root'@'%';
FLUSH PRIVILEGES;
