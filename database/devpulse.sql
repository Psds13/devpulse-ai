-- ==============================================================
-- CRIAÇÃO DO SCHEMA
-- ==============================================================

CREATE SCHEMA IF NOT EXISTS devpulse;

-- ==============================================================
-- TABELAS
-- ==============================================================

-- Tabela: devpulse.repositories
CREATE TABLE IF NOT EXISTS devpulse.repositories (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    owner VARCHAR NOT NULL,
    url VARCHAR UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela: devpulse.analysis_reports
CREATE TABLE IF NOT EXISTS devpulse.analysis_reports (
    id SERIAL PRIMARY KEY,
    repository_id INTEGER REFERENCES devpulse.repositories(id) ON DELETE CASCADE,
    commit_sha VARCHAR,
    issues_found JSONB NOT NULL DEFAULT '[]'::jsonb,
    ai_suggestions JSONB NOT NULL DEFAULT '{}'::jsonb,
    quality_score INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================================
-- SEGURANÇA
-- ==============================================================

-- Criar usuário
CREATE USER devpulse_api_user WITH PASSWORD '123456';

-- Conceder permissões no schema
GRANT USAGE ON SCHEMA devpulse TO devpulse_api_user;

-- Conceder permissões nas tabelas
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE 
    devpulse.repositories, 
    devpulse.analysis_reports 
TO devpulse_api_user;

-- Conceder permissões nas sequências
GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA devpulse TO devpulse_api_user;