-- ============================================================
-- Kenya Crop Yield App – Supabase Schema
-- Run this in the Supabase SQL editor
-- ============================================================

-- 1. Users table (custom, separate from auth.users)
CREATE TABLE IF NOT EXISTS app_users (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username    TEXT UNIQUE NOT NULL,
    email       TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Predictions log
CREATE TABLE IF NOT EXISTS predictions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES app_users(id) ON DELETE CASCADE,
    username        TEXT,
    region          TEXT,
    crop            TEXT,
    rainfall_mm     FLOAT,
    temperature_c   FLOAT,
    humidity_pct    FLOAT,
    soil_ph         FLOAT,
    soil_texture    TEXT,
    soil_saturation FLOAT,
    land_size       FLOAT,
    predicted_yield FLOAT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS predictions_user_idx ON predictions(user_id);
CREATE INDEX IF NOT EXISTS predictions_created_idx ON predictions(created_at DESC);

-- Row Level Security (RLS) – optional but recommended
ALTER TABLE app_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE predictions ENABLE ROW LEVEL SECURITY;

-- Public read for predictions (dashboard), restricted write
CREATE POLICY "Allow insert predictions" ON predictions FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow read predictions"   ON predictions FOR SELECT USING (true);
CREATE POLICY "Allow insert users"       ON app_users   FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow read users"         ON app_users   FOR SELECT USING (true);
