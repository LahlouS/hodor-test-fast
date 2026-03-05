-- database/migrations/01_agents_services_logs.sql
-- SQL Migration for Agents, Services, Agent-Service Permissions, and Logs

-- STEP 1: Ensure pgcrypto is enabled for UUID generation (safe if already enabled)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- STEP 2: Create permission enum (idempotent)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'agent_service_permission') THEN
        CREATE TYPE agent_service_permission AS ENUM ('admin', 'member', 'observer');
    END IF;
END$$;

-- STEP 3: Create 'agents' table
CREATE TABLE IF NOT EXISTS agents (
    agent_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    name       TEXT NOT NULL,
    is_active  BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_agents_user_id ON agents(user_id);
CREATE INDEX IF NOT EXISTS idx_agents_is_active ON agents(is_active);

-- STEP 4: Create 'services' table (mock external services)
CREATE TABLE IF NOT EXISTS services (
    service_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name       TEXT NOT NULL UNIQUE,
    manifest   JSONB NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_services_name ON services(name);
CREATE INDEX IF NOT EXISTS idx_services_manifest_gin ON services USING GIN (manifest);

-- STEP 5: Create 'agent_service' join table
CREATE TABLE IF NOT EXISTS agent_service (
    agent_id    UUID NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,
    service_id  UUID NOT NULL REFERENCES services(service_id) ON DELETE CASCADE,
    permission  agent_service_permission NOT NULL DEFAULT 'member',
    PRIMARY KEY (agent_id, service_id)
);

CREATE INDEX IF NOT EXISTS idx_agent_service_service_id ON agent_service(service_id);
CREATE INDEX IF NOT EXISTS idx_agent_service_permission ON agent_service(permission);

-- STEP 6: Create 'logs' table
CREATE TABLE IF NOT EXISTS logs (
    log_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id      UUID NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,
    service_id    UUID NOT NULL REFERENCES services(service_id) ON DELETE CASCADE,
    endpoint      TEXT NOT NULL,
    log_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_success    BOOLEAN NOT NULL,
    message       TEXT
);

CREATE INDEX IF NOT EXISTS idx_logs_agent_id ON logs(agent_id);
CREATE INDEX IF NOT EXISTS idx_logs_service_id ON logs(service_id);
CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(log_timestamp);
CREATE INDEX IF NOT EXISTS idx_logs_agent_service_time ON logs(agent_id, service_id, log_timestamp);