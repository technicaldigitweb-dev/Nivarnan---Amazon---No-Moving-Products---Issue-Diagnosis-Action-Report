#!/usr/bin/env bash
# run_anpia_daily.sh -- REQ-ANPIA-REQ-01-D02
#
# Entry point invoked by the systemd service (or the cron fallback) to run
# one ANPIA daily publication attempt. Not installed or scheduled by this
# task -- see 05_IMPLEMENTATION/deployment/README.md.
#
# Responsibilities kept deliberately thin: resolve paths, activate the venv
# if present, exec the pipeline with --publish. All real safety logic
# (locking, gates, validation, exit codes) lives in anpia_daily_pipeline.py
# itself -- this script does not duplicate or bypass any of it.

set -euo pipefail

# -- Explicit, non-guessed paths (fill in for the real deployment target) --
PROJECT_ROOT="${ANPIA_PROJECT_ROOT:?ANPIA_PROJECT_ROOT must be set explicitly -- refuse to guess a working directory}"
PYTHON_BIN="${ANPIA_PYTHON_BIN:-python3}"
ENV_FILE="${ANPIA_ENV_FILE:?ANPIA_ENV_FILE must be set explicitly (path to the protected .env) -- refuse to guess a credential location}"

if [ ! -d "$PROJECT_ROOT" ]; then
  echo "FATAL: ANPIA_PROJECT_ROOT does not exist: $PROJECT_ROOT" >&2
  exit 6
fi
if [ ! -f "$ENV_FILE" ]; then
  echo "FATAL: ANPIA_ENV_FILE does not exist: $ENV_FILE" >&2
  exit 6
fi

cd "$PROJECT_ROOT"

# anpia_config.py reads PROJECT_ROOT/.env by convention. If the protected
# env file lives elsewhere on the deployment target, symlink or copy it to
# PROJECT_ROOT/.env as part of deployment -- this script does not silently
# relocate or copy credential files itself.
if [ ! -f "$PROJECT_ROOT/.env" ]; then
  echo "FATAL: expected .env at $PROJECT_ROOT/.env -- ANPIA_ENV_FILE ($ENV_FILE) must be linked there during deployment, not passed as a free-floating path." >&2
  exit 6
fi

exec "$PYTHON_BIN" "$PROJECT_ROOT/05_IMPLEMENTATION/anpia_daily_pipeline.py" \
  --publish \
  --trigger-source scheduled \
  --confirmation-token "PUBLISH_NIVARNAN_ANPIA"
