# API Contract Draft

The desktop app is local-first. These endpoints are for remote management and sync.

## Auth

### `POST /auth/login`

Request:

```json
{
  "program_id": "AB12CD34",
  "parent_password": "secret"
}
```

Response:

```json
{
  "ok": true,
  "session_token": "opaque-token",
  "program_id": "AB12CD34"
}
```

## Dashboard

### `GET /dashboard`

Headers:

- `Authorization: Bearer <session_token>`

Response:

```json
{
  "program_id": "AB12CD34",
  "settings": {},
  "stats": {},
  "counts": {}
}
```

## Content

### `GET /content`

Returns spheres, levels, topics, lesson blocks, tasks, answers, options, and assets metadata.

## Settings

### `PUT /settings`

Updates remote settings for one program.

## Content Editing

### `PUT /topics/{id}`

Updates topic titles, descriptions, and the first lesson block.

### `PUT /tasks/{id}`

Updates task prompts, accepted answers, options, and metadata.

## Sync

### `POST /sync/push`

Pushes local mutations to the server.

### `POST /sync/pull`

Pulls remote mutations since the last known sync checkpoint.
