#!/usr/bin/env zsh

# Start mock SMTP server in background, then run Streamlit app
SMTP_PORT=${SMTP_PORT:-1025}
UV_BIN=${UV_BIN:-uv}

print "Starting mock SMTP server on localhost:${SMTP_PORT}…"
${UV_BIN} run python src/infrastructure/tools/mock_smtp_server.py &!
SMTP_PID=$!

cleanup() {
  print "\nStopping mock SMTP server (pid: ${SMTP_PID})…"
  if [[ -n "${SMTP_PID}" ]]; then
    kill ${SMTP_PID} 2>/dev/null || true
    wait ${SMTP_PID} 2>/dev/null || true
  fi
}
trap cleanup INT TERM EXIT

sleep 0.3
print "Starting Streamlit app…"
${UV_BIN} run streamlit run src/app.py

# Cleanup runs automatically via trap when Streamlit exits
