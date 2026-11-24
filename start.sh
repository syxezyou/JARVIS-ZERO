#!/usr/bin/env bash
set -e
cd /home/container 2>/dev/null || cd "$(dirname "$0")"
exec python -m uvicorn app:app --host 0.0.0.0 --port "${SERVER_PORT:-${PORT:-8000}}"
