-- Connexion en tant qu'administrateur PostgreSQL
CREATE DATABASE titanic_db;
CREATE USER titanic_user WITH PASSWORD 'titanic_password';
GRANT ALL PRIVILEGES ON DATABASE titanic_db TO titanic_user;

-- Se connecter à la base titanic_db
\c titanic_db;

-- Donner les permissions sur le schéma public
GRANT ALL ON SCHEMA public TO titanic_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO titanic_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO titanic_user;