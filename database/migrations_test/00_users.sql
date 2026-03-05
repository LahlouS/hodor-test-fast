-- database/migrations/00_users.sql
-- SQL Migration for Users

-- STEP 1: Enable pgcrypto for UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- STEP 2: Create the 'users' table with automatic UUID

CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL,
    hash_password TEXT NOT NULL
);