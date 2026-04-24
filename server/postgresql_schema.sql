BEGIN;

CREATE TABLE IF NOT EXISTS programs (
    id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    locale TEXT NOT NULL DEFAULT 'ru',
    parent_password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_sync_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS program_settings (
    program_id TEXT NOT NULL REFERENCES programs(id) ON DELETE CASCADE,
    key TEXT NOT NULL,
    value_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (program_id, key)
);

CREATE TABLE IF NOT EXISTS spheres (
    id TEXT PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    sort_order INTEGER NOT NULL DEFAULT 0,
    title_ru TEXT NOT NULL,
    title_pl TEXT NOT NULL,
    title_en TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS levels (
    id TEXT PRIMARY KEY,
    sphere_id TEXT NOT NULL REFERENCES spheres(id) ON DELETE CASCADE,
    code TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    title_ru TEXT NOT NULL,
    title_pl TEXT NOT NULL,
    title_en TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (sphere_id, code)
);

CREATE TABLE IF NOT EXISTS topics (
    id TEXT PRIMARY KEY,
    sphere_id TEXT NOT NULL REFERENCES spheres(id) ON DELETE CASCADE,
    level_id TEXT REFERENCES levels(id) ON DELETE SET NULL,
    slug TEXT NOT NULL,
    mode TEXT NOT NULL,
    grade INTEGER,
    theme TEXT,
    sort_order INTEGER NOT NULL DEFAULT 0,
    title_ru TEXT NOT NULL,
    title_pl TEXT NOT NULL,
    title_en TEXT NOT NULL,
    description_ru TEXT NOT NULL,
    description_pl TEXT NOT NULL,
    description_en TEXT NOT NULL,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS lesson_blocks (
    id TEXT PRIMARY KEY,
    topic_id TEXT NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    sort_order INTEGER NOT NULL DEFAULT 0,
    kind TEXT NOT NULL DEFAULT 'intro',
    title_ru TEXT NOT NULL,
    title_pl TEXT NOT NULL,
    title_en TEXT NOT NULL,
    content_ru TEXT NOT NULL,
    content_pl TEXT NOT NULL,
    content_en TEXT NOT NULL,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    topic_id TEXT NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    sort_order INTEGER NOT NULL DEFAULT 0,
    mode TEXT NOT NULL,
    grade INTEGER,
    theme TEXT,
    task_type TEXT NOT NULL,
    hint_type TEXT NOT NULL DEFAULT 'math',
    source TEXT NOT NULL DEFAULT 'built_in',
    title_ru TEXT NOT NULL,
    title_pl TEXT NOT NULL,
    title_en TEXT NOT NULL DEFAULT '',
    prompt_ru TEXT NOT NULL,
    prompt_pl TEXT NOT NULL,
    prompt_en TEXT NOT NULL DEFAULT '',
    answer_display TEXT NOT NULL DEFAULT '',
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS accepted_answers (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    answer_value TEXT NOT NULL,
    normalized_value TEXT NOT NULL,
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS task_options (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    sort_order INTEGER NOT NULL DEFAULT 0,
    option_value TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS assets (
    id TEXT PRIMARY KEY,
    topic_id TEXT REFERENCES topics(id) ON DELETE SET NULL,
    sphere_id TEXT REFERENCES spheres(id) ON DELETE SET NULL,
    kind TEXT NOT NULL,
    storage_key TEXT NOT NULL UNIQUE,
    original_name TEXT NOT NULL,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS stats_summary (
    program_id TEXT PRIMARY KEY REFERENCES programs(id) ON DELETE CASCADE,
    coins INTEGER NOT NULL DEFAULT 0,
    correct INTEGER NOT NULL DEFAULT 0,
    wrong INTEGER NOT NULL DEFAULT 0,
    completed_breaks INTEGER NOT NULL DEFAULT 0,
    adult_completed INTEGER NOT NULL DEFAULT 0,
    child_completed INTEGER NOT NULL DEFAULT 0,
    memory_completed INTEGER NOT NULL DEFAULT 0,
    last_mode TEXT NOT NULL DEFAULT '',
    last_activity TEXT NOT NULL DEFAULT '',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS stats_events (
    id TEXT PRIMARY KEY,
    program_id TEXT NOT NULL REFERENCES programs(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    event_payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    synced_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS sync_state (
    program_id TEXT NOT NULL REFERENCES programs(id) ON DELETE CASCADE,
    key TEXT NOT NULL,
    value_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (program_id, key)
);

CREATE INDEX IF NOT EXISTS idx_topics_mode_grade
ON topics(mode, grade, sort_order);

CREATE INDEX IF NOT EXISTS idx_tasks_topic_order
ON tasks(topic_id, sort_order);

CREATE INDEX IF NOT EXISTS idx_lesson_blocks_topic_order
ON lesson_blocks(topic_id, sort_order);

CREATE INDEX IF NOT EXISTS idx_assets_scope
ON assets(sphere_id, topic_id, kind, storage_key);

CREATE INDEX IF NOT EXISTS idx_stats_events_program_created
ON stats_events(program_id, created_at DESC);

CREATE TABLE IF NOT EXISTS remote_program_snapshots (
    program_id TEXT PRIMARY KEY,
    parent_password_hash TEXT NOT NULL,
    device_id TEXT NOT NULL DEFAULT '',
    checkpoint TEXT NOT NULL DEFAULT '',
    snapshot_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS remote_sessions (
    token_hash TEXT PRIMARY KEY,
    program_id TEXT NOT NULL REFERENCES remote_program_snapshots(program_id) ON DELETE CASCADE,
    ip_address TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS api_idempotency_keys (
    scope TEXT NOT NULL,
    key TEXT NOT NULL,
    fingerprint TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    response_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (scope, key)
);

CREATE TABLE IF NOT EXISTS backend_audit_log (
    id BIGSERIAL PRIMARY KEY,
    event_type TEXT NOT NULL,
    ip_address TEXT NOT NULL DEFAULT '',
    program_id TEXT NOT NULL DEFAULT '',
    success BOOLEAN NOT NULL DEFAULT TRUE,
    details_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS rate_limit_hits (
    id BIGSERIAL PRIMARY KEY,
    ip_address TEXT NOT NULL,
    bucket TEXT NOT NULL,
    route TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS rate_limit_violations (
    id BIGSERIAL PRIMARY KEY,
    ip_address TEXT NOT NULL,
    bucket TEXT NOT NULL,
    route TEXT NOT NULL,
    details_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ip_bans (
    ip_address TEXT PRIMARY KEY,
    reason TEXT NOT NULL,
    ban_until TIMESTAMPTZ NOT NULL,
    details_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_remote_program_snapshots_updated
ON remote_program_snapshots(updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_remote_sessions_expires
ON remote_sessions(expires_at);

CREATE INDEX IF NOT EXISTS idx_api_idempotency_expires
ON api_idempotency_keys(expires_at);

CREATE INDEX IF NOT EXISTS idx_backend_audit_log_event_created
ON backend_audit_log(event_type, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_backend_audit_log_ip_created
ON backend_audit_log(ip_address, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_rate_limit_hits_lookup
ON rate_limit_hits(ip_address, bucket, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_rate_limit_violations_lookup
ON rate_limit_violations(ip_address, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_ip_bans_until
ON ip_bans(ban_until DESC);

COMMIT;
