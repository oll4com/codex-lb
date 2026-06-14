from pathlib import Path

HELPERS_FILE = Path('/app/app/modules/proxy/helpers.py')

TRANSIENT_SET_TARGET = (
    '_TRANSIENT_CODES = frozenset({"server_error", "upstream_error", "stream_incomplete", '
    '"server_is_overloaded", "model_is_at_capacity", "selected_model_is_at_capacity", '
    '"model_at_capacity", "capacity_exceeded"})\n'
)

CANDIDATES = [
    '_TRANSIENT_CODES = frozenset({"server_error", "upstream_error", "stream_incomplete"})\n',
    '_TRANSIENT_CODES = frozenset({"server_error", "upstream_error", "stream_incomplete", "server_is_overloaded"})\n',
]

content = HELPERS_FILE.read_text()
if TRANSIENT_SET_TARGET in content:
    print('already patched', HELPERS_FILE)
    raise SystemExit(0)

for old in CANDIDATES:
    if old in content:
        content = content.replace(old, TRANSIENT_SET_TARGET, 1)
        HELPERS_FILE.write_text(content)
        print('patched', HELPERS_FILE)
        raise SystemExit(0)

raise SystemExit('target snippet not found: transient code list')
