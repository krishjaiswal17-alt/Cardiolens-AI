-- CardioLens Gym Platform - Database Schema
-- Requires PostgreSQL + TimescaleDB + pgvector

-- Create vector extension for facial embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Users Table (Identity & Profile)
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    face_embedding VECTOR(512), -- For DeepFace/FaceNet identity matching
    name VARCHAR(255),
    contact_number VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Scans Table (TimescaleDB Hypertable)
CREATE TABLE IF NOT EXISTS scans (
    scan_id UUID DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    scan_type VARCHAR(10) CHECK (scan_type IN ('entry', 'exit')),
    hr_bpm DECIMAL(5,2),
    hrv_ms DECIMAL(5,2),
    stress_level_rppg DECIMAL(5,2),
    PRIMARY KEY (scan_id, timestamp)
);

-- Convert standard table to TimescaleDB Hypertable for high-frequency time-series optimized querying
SELECT create_hypertable('scans', 'timestamp');

-- Indexes
CREATE INDEX ix_scans_user_time ON scans (user_id, timestamp DESC);

-- Wellness Risk Flags Table (Generated after Exit Evaluation)
CREATE TABLE risk_flags (
    flag_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id),
    exit_scan_id UUID,
    flag_type VARCHAR(50), -- e.g., 'HR Recovery Delay', 'Severe HRV Drop'
    severity VARCHAR(20), -- e.g., 'moderate', 'high'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
