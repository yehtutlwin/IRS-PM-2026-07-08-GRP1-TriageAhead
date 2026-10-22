#!/usr/bin/env bash
# Run the interview web app with a throwaway public address, so a phone can scan the QR code of an app running on
# your machine. Uses a Cloudflare "quick tunnel": no account, no key, a new random https address every start.
#
#   bash webapp/run.sh        prints the address and a QR code of it in the terminal; Ctrl-C stops the app and the tunnel
#
# Needs the cloudflared binary once per machine: https://github.com/cloudflare/cloudflared/releases
# (macOS: brew install cloudflared; Debian/Ubuntu, and Windows under WSL2: the amd64 .deb from that page).
# Without a tunnel just run `.venv/bin/python webapp/server.py`; this script adds nothing else.
# Port: WEBAPP_PORT (default 8090). Model: LLM_BACKEND and keys from .env, read by the app itself.
# The app builds every link and QR code from the address the browser used (Host and X-Forwarded-Proto headers),
# so nothing is configured for the tunnel. Anyone with the address can open the chat while it runs; stop it after the test.
set -e
cd "$(dirname "$0")/.."
PORT="${WEBAPP_PORT:-8090}"; export WEBAPP_PORT="$PORT"
PY=.venv/bin/python; [ -x "$PY" ] || PY=python3
CF="$(command -v cloudflared 2>/dev/null || true)"; [ -n "$CF" ] || [ ! -x "$HOME/.local/bin/cloudflared" ] || CF="$HOME/.local/bin/cloudflared"
[ -n "$CF" ] || { echo "cloudflared not found: install it from https://github.com/cloudflare/cloudflared/releases and run this again."; exit 1; }

OUT=prototype/out; mkdir -p "$OUT"; TLOG="$OUT/tunnel.log"; : > "$TLOG"
"$PY" webapp/server.py &
SRV=$!
cleanup() { kill "$SRV" 2>/dev/null; [ -n "${TUN:-}" ] && kill "$TUN" 2>/dev/null; wait 2>/dev/null; }
trap cleanup EXIT INT TERM
sleep 1
"$CF" tunnel --no-autoupdate --url "http://localhost:$PORT" > "$TLOG" 2>&1 &
TUN=$!
URL=""
for _ in $(seq 1 60); do
  URL="$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' "$TLOG" | head -1 || true)"; [ -n "$URL" ] && break
  kill -0 "$TUN" 2>/dev/null || break; sleep 0.5
done
if [ -z "$URL" ]; then echo "the tunnel gave no address; its log ($TLOG) says:"; tail -5 "$TLOG"; exit 1; fi

echo; echo "Local:  http://localhost:$PORT"; echo "Phone:  $URL"; echo
"$PY" - "$URL" <<'PYEOF' 2>/dev/null || true
import sys
try:
    import segno; segno.make(sys.argv[1]).terminal(compact=True)
except ImportError: print("(install segno to see the QR code here; the address above works as typed)")
PYEOF
echo; echo "Scan with the phone, or type the address. Caregiver chat at /; the nurse report opens from the QR code in the chat."
echo "Ctrl-C stops the app and the tunnel."
wait "$SRV"
