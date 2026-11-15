#!/usr/bin/env bash
# Start registry-service, weather-service, planner-service and the frontend together.
# Ctrl-C stops all four. Every log line is prefixed with the service name.
#
# Ports (override with environment variables):
#   REGISTRY_PORT=8000  WEATHER_PORT=8001  PLANNER_PORT=8002  FRONTEND_PORT=3000
# The script wires the services to each other with those ports. Everything else
# (timeouts, provider URL, database) comes from each service's own .env file.
# A missing .env is created from .env.example (the frontend uses .env.local).

set -uo pipefail
set -m  # each service gets its own process group, so Ctrl-C can stop its whole tree

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REGISTRY_PORT="${REGISTRY_PORT:-8000}"
WEATHER_PORT="${WEATHER_PORT:-8001}"
PLANNER_PORT="${PLANNER_PORT:-8002}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"
STARTUP_SECONDS="${STARTUP_SECONDS:-90}"

REGISTRY_URL="http://127.0.0.1:$REGISTRY_PORT"
WEATHER_URL="http://127.0.0.1:$WEATHER_PORT"
PLANNER_URL="http://127.0.0.1:$PLANNER_PORT"

PIDS=()
NAMES=()

fail() { echo "error: $*" >&2; exit 1; }

for tool in uv node npm curl ss; do
  command -v "$tool" >/dev/null || fail "$tool is required but not installed"
done

port_in_use() { [[ -n "$(ss -ltnH "sport = :$1")" ]]; }

for entry in "registry:$REGISTRY_PORT" "weather:$WEATHER_PORT" "planner:$PLANNER_PORT" "frontend:$FRONTEND_PORT"; do
  name="${entry%%:*}"
  port_in_use "${entry#*:}" && fail "port ${entry#*:} ($name) is already in use. Stop what is using it, or set ${name^^}_PORT."
done

ensure_env() {  # ensure_env <service dir> <env file> <example file>
  local target="$ROOT/services/$1/$2"
  if [[ ! -f "$target" ]]; then
    cp "$ROOT/services/$1/$3" "$target" || fail "cannot create $1/$2"
    echo "created services/$1/$2 from $3 (edit it if you need other values)"
  fi
}
ensure_env weather-service .env .env.example
ensure_env planner-service .env .env.example
ensure_env frontend .env.local .env.example
[[ -d "$ROOT/services/frontend/node_modules" ]] || (cd "$ROOT/services/frontend" && npm install) || fail "npm install failed"

start() {  # start <name> <service dir> <command...>
  local name="$1" dir="$2"
  shift 2
  ( cd "$ROOT/services/$dir" && exec "$@" ) > >(sed -u "s/^/[$name] /") 2>&1 &
  PIDS+=("$!")
  NAMES+=("$name")
}

cleanup() {
  trap - INT TERM EXIT
  echo
  echo "Stopping services"
  for pid in "${PIDS[@]}"; do kill -- "-$pid" 2>/dev/null; done
  wait 2>/dev/null
}
trap cleanup INT TERM EXIT

start registry registry-service \
  uv run --no-active uvicorn main:app --host 127.0.0.1 --port "$REGISTRY_PORT"
start weather weather-service \
  uv run --no-active uvicorn main:app --host 127.0.0.1 --port "$WEATHER_PORT"
start planner planner-service \
  env REGISTRY_URL="$REGISTRY_URL" WEATHER_URL="$WEATHER_URL" \
  uv run --no-active uvicorn main:app --host 127.0.0.1 --port "$PLANNER_PORT"
start frontend frontend \
  env REGISTRY_URL="$REGISTRY_URL" WEATHER_URL="$WEATHER_URL" PLANNER_URL="$PLANNER_URL" \
  npm run dev -- --port "$FRONTEND_PORT"

wait_until_up() {  # wait_until_up <name> <url>
  local deadline=$((SECONDS + STARTUP_SECONDS))
  until curl -sf -o /dev/null "$2"; do
    ((SECONDS >= deadline)) && fail "$1 did not answer at $2 within ${STARTUP_SECONDS}s (see its log lines above)"
    for i in "${!PIDS[@]}"; do
      kill -0 "${PIDS[$i]}" 2>/dev/null || fail "${NAMES[$i]} stopped while starting (see its log lines above)"
    done
    sleep 0.5
  done
}
wait_until_up registry "$REGISTRY_URL/health"
wait_until_up weather "$WEATHER_URL/health"
wait_until_up planner "$PLANNER_URL/health"
wait_until_up frontend "http://127.0.0.1:$FRONTEND_PORT/"

cat <<EOF

AgroPilot is running. Ctrl-C stops everything.
  frontend  http://localhost:$FRONTEND_PORT
  registry  $REGISTRY_URL/docs
  weather   $WEATHER_URL/docs
  planner   $PLANNER_URL/docs
EOF

# Stay up until one service exits, then say which and stop the rest.
wait -n
for i in "${!PIDS[@]}"; do
  kill -0 "${PIDS[$i]}" 2>/dev/null || echo "error: ${NAMES[$i]} stopped" >&2
done
exit 1
