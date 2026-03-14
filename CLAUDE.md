# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Synapse-Workvivo is an HR chatbot ("Iris Bot") integrated with the Workvivo messaging platform. It answers HCM (Human Capital Management) questions using Azure Custom Question Answering (CQA) as the knowledge base, with escalation flows that email HR when the bot can't help. The app also generates weekly analytics reports from Azure Log Analytics and a MySQL database.

## Commands

### Development
```bash
# Activate virtual environment
source workvivo/bin/activate  # bundled venv in repo

# Run the Flask app (primary)
gunicorn --bind 0.0.0.0:8080 app:app

# Run with uvicorn (alternative, for main.py FastAPI version)
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Deployment
```bash
# Deploy to AWS App Runner via ECR
./deploy.sh  # Builds Docker image, tags, and pushes to ECR (ap-southeast-1)
```

### Environment
Requires `.env` file in project root. Key variables:
- `WORKVIVO_API_URL`, `WORKVIVO_ID`, `WORKVIVO_TOKEN` — Workvivo Bot API
- `AZURE_BOT_URL`, `AZURE_BOT_AUTH_TOKEN` — Azure CQA endpoint
- `SENDGRID_API_KEY`, `SENDER_EMAIL` — Email escalation via SendGrid
- `RDS_HOST`, `RDS_USER`, `RDS_PASSWORD`, `RDS_DB_NAME` — MySQL (AWS RDS)
- `TENANT_ID`, `CLIENT_ID`, `CLIENT_SECRET`, `WORKSPACE_ID` — Azure Log Analytics
- `ECHO_BOT` (bool string), `GAME_MODE` (bool string), `DEBUG_MODE` (bool string)
- `SUGGESTIONS_THRESHOLD`, `MASK_URL` (bool string)

## Architecture

### Two Entry Points
- **`app.py`** (Flask, production) — Webhook receiver, analytics endpoints, email attachment sender. Deployed via Gunicorn on port 8080.
- **`main.py`** (FastAPI, legacy/testing) — Simplified webhook with echo/card/quick-reply demos. Not used in production.

### Request Flow
```
Workvivo → POST /webhook → app.py → utils.respond()
                                       ├── Duplicate message check (in-memory dict)
                                       ├── Redirection pipeline (emails, comments, numbers, special messages)
                                       └── azure_bot.azure_bot_response_cqa() → Azure CQA
                                             └── postprocess_azure_response_v2() → Workvivo reply
```

### Key Modules (`utility/`)
- **`utils.py`** — Core bot logic: message routing, response formatting, escalation flows, Workvivo message sending. Maintains in-memory state (`users_chat_data_holder`, `users_not_satisfied`, `no_bot_match`).
- **`azure_bot.py`** — Calls Azure Custom Question Answering API. Includes response format transformer (`transform_to_qnamaker_format`) and optional cache.
- **`config.py`** — All configuration: Azure credentials, bot response phrases, thresholds, email settings. `score_threshold=80`, escalation `threshold=3`.
- **`mail_service_v2.py`** — SendGrid email sending + weekly analytics report generation. Queries Azure Log Analytics, MySQL tables, builds multi-sheet Excel report.
- **`db_utils.py`** — MySQL (PyMySQL) database access. Tables: `user_comments`, `user_escalations`, `user_not_satisfied`, `game_reports`, `user_cache_logs`, `artefacts`, `quiz_data`.
- **`workvivo.py`** — Workvivo user API calls (get user data, fetch email by user ID, with caching).
- **`datastructures.py`** — Workvivo message formatters (`WORKVIVO_FORMATTER`), user session tracker (`DATA_COLLECTOR`), Azure bot response cache (`azure_bot_cache_v2`), Flask form (`InfoForm`).
- **`azure_log_analytics.py`** — Queries Azure Log Analytics workspace using KQL for chatbot usage logs.
- **`gameplay.py`** — Optional quiz game mode (toggled by `GAME_MODE` env var).
- **`attachments.py`** — Static mapping of attachment IDs to Workvivo document URLs.
- **`aws.py`** — S3 file download helper for email attachments.

### Escalation Logic
The bot tracks user dissatisfaction via in-memory counters. After 3 consecutive "No" responses or 3 unmatched queries, it emails HR with the chat log and resets the user's session. The `find_three_consecutive_no()` and `find_three_consecutive_not_found()` functions check chat history patterns.

### Analytics Pipeline
`/iris_analytics_trigger` (GET, auth-protected) and `/iris_analytics` (form-based) trigger `consolidated_analytics()` which:
1. Pulls chat logs from Azure Log Analytics
2. Pulls escalation/feedback/game data from MySQL
3. Merges cached query data
4. Generates multi-sheet Excel report (queries, unique users, scores, escalations, feedback, top questions)

### Workvivo Message Types
Messages sent via Workvivo Bot API support: `message` (text), `quick_reply` (buttons), `card` (rich cards with images/buttons/links). The `WORKVIVO_FORMATTER` class handles all format conversions.

## Important Patterns
- **In-memory state**: User sessions, satisfaction counters, and game state are stored in module-level dicts — not persisted. Server restart clears all state.
- **Duplicate detection**: `user_last_messages` dict in `app.py` skips duplicate consecutive messages per user.
- **Timezone**: All timestamps use `Asia/Singapore` (SGT).
- **Version tracking**: `docs/version_history.json` tracks releases, exposed via `GET /health`.
- **Cache**: Bot response cache stored at `/tmp/cache.json`, clearable via `GET /clear_cache`.
- **`old_app.py`**: Previous version that supported Facebook Workplace. Kept for reference.
