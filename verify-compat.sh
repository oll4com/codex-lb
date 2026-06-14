#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-http://127.0.0.1:2455}"
CONTAINER_NAME="${CONTAINER_NAME:-codex-lb}"

check_json_key() {
  local path="$1"
  local key="$2"
  local body
  body="$(curl -fsS "${BASE_URL}${path}")"
  JSON_BODY="$body" python3 - "$path" "$key" <<'PY'
import json
import os
import sys

path = sys.argv[1]
key = sys.argv[2]
data = json.loads(os.environ["JSON_BODY"])
current = data
for part in key.split("."):
    if isinstance(current, dict) and part in current:
        current = current[part]
    else:
        raise SystemExit(f"{path} missing key {key}")
print(f"OK {path} -> {key}")
PY
}

check_models_payload() {
  local path="$1"
  local body
  body="$(curl -fsS "${BASE_URL}${path}")"
  JSON_BODY="$body" python3 - "$path" <<'PY'
import json
import os
import sys

path = sys.argv[1]
data = json.loads(os.environ["JSON_BODY"])
models = data.get("models")
if not isinstance(models, list):
    raise SystemExit(f"{path} missing models list")
print(f"OK {path} -> models={len(models)}")
PY
}

first_model_slug() {
  JSON_BODY="$(curl -fsS "${BASE_URL}/api/v1/models")" python3 - <<'PY'
import json
import os
import sys

data = json.loads(os.environ["JSON_BODY"])
models = data.get("models") or []
if not models:
    raise SystemExit("no models returned from /api/v1/models")
first = models[0]
slug = first.get("slug") or first.get("id") or first.get("model")
if not slug:
    raise SystemExit("first model missing slug/id/model")
print(slug)
PY
}

check_json_key "/version" "version"
check_json_key "/props" "compatibility.openai_responses"
check_json_key "/v1/props" "compatibility.openai_chat_completions"
check_models_payload "/api/v1/models"
check_models_payload "/api/tags"

if [[ -n "${CODEX_LB_API_KEY:-}" ]]; then
  model_slug="$(first_model_slug)"
  response_body="$(curl -fsS \
    -H "Authorization: Bearer ${CODEX_LB_API_KEY}" \
    -H 'Content-Type: application/json' \
    -d "{\"model\":\"${model_slug}\",\"input\":\"Reply with exactly OK\",\"max_output_tokens\":16}" \
    "${BASE_URL}/v1/responses")"
  JSON_BODY="$response_body" python3 - <<'PY'
import json
import os
import sys

data = json.loads(os.environ["JSON_BODY"])
output = data.get("output")
if not isinstance(output, list):
    raise SystemExit("/v1/responses missing output list")
print("OK /v1/responses authenticated smoke")
PY
else
  echo "SKIP /v1/responses authenticated smoke (set CODEX_LB_API_KEY to enable)"
fi

recent_logs="$(docker logs --since 5m "${CONTAINER_NAME}" 2>&1 || true)"
if printf '%s\n' "$recent_logs" | grep -Eq 'Unsupported parameter: truncation|GET /api/v1/models HTTP/1.1" 404|GET /api/tags HTTP/1.1" 404|GET /v1/props HTTP/1.1" 404'; then
  echo "$recent_logs" >&2
  echo "compat verification failed: found post-check errors in logs" >&2
  exit 1
fi

echo "Compatibility verification passed for ${BASE_URL}"
