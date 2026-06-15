#!/usr/bin/env bash
# Start server in background then launch a local client.
# Usage:
#   ./run.sh              — solo / host
#   ./run.sh <server-ip>  — join a remote game (skips starting server)

set -e
cd "$(dirname "$0")"

if [[ -z "$1" ]]; then
    echo "Starting server..."
    python3 server.py &
    SERVER_PID=$!
    sleep 0.4
    trap "kill $SERVER_PID 2>/dev/null" EXIT
    python3 client.py
else
    python3 client.py "$1"
fi
