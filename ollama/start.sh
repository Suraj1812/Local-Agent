#!/bin/sh
set -eu

MODEL="${OLLAMA_MODEL:-qwen2.5:0.5b}"
export OLLAMA_HOST="${OLLAMA_HOST:-0.0.0.0:11434}"

ollama serve &
SERVER_PID="$!"

attempt=0
until OLLAMA_HOST=http://127.0.0.1:11434 ollama list >/dev/null 2>&1; do
  attempt=$((attempt + 1))
  if [ "$attempt" -ge 90 ]; then
    echo "Ollama did not become ready in time."
    exit 1
  fi
  sleep 1
done

if ! OLLAMA_HOST=http://127.0.0.1:11434 ollama list | grep -q "^${MODEL}[[:space:]]"; then
  OLLAMA_HOST=http://127.0.0.1:11434 ollama pull "$MODEL"
fi

wait "$SERVER_PID"
