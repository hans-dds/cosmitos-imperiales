#!/usr/bin/env sh
set -eu

SMTP_PORT="${SMTP_PORT:-1025}"
STREAMLIT_PORT="${STREAMLIT_SERVER_PORT:-8501}"

echo "Starting mock SMTP server on localhost:${SMTP_PORT}…"
python src/infrastructure/tools/mock_smtp_server.py &
SMTP_PID=$!

cleanup() {
  echo "Stopping mock SMTP server (pid: ${SMTP_PID})…"
  if [ -n "${SMTP_PID}" ]; then
    kill ${SMTP_PID} 2>/dev/null || true
    wait ${SMTP_PID} 2>/dev/null || true
  fi
}
trap cleanup INT TERM EXIT

echo "Waiting for SMTP server to be ready on localhost:${SMTP_PORT}…"
# Wait until the SMTP port is accepting connections (max ~10s)
for i in $(seq 1 40); do
  python - <<'PY'
import socket, os, sys
host = 'localhost'
port = int(os.getenv('SMTP_PORT', '1025'))
s = socket.socket()
s.settimeout(0.25)
try:
    s.connect((host, port))
    print('ready')
except Exception:
    pass
finally:
    s.close()
PY
  if [ "$?" -eq 0 ]; then
    break
  fi
  sleep 0.25
done

echo "Starting Streamlit app on port ${STREAMLIT_PORT}…"
exec streamlit run src/app.py
