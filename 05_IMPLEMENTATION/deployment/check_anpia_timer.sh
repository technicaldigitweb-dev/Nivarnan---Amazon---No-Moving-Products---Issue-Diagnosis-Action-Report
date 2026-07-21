#!/usr/bin/env bash
# check_anpia_timer.sh -- REQ-ANPIA-REQ-01-D02
#
# Read-only diagnostic. Safe to run at any time (before or after install) --
# never modifies system state. Verifies the calendar spec is understood
# correctly by the target's systemd version, without requiring the unit to
# actually be installed.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== systemd version ==="
systemctl --version | head -1

echo ""
echo "=== Calendar spec validation (does NOT require the unit to be installed) ==="
echo "Spec under test: *-*-* 12:00:00 Asia/Colombo"
if command -v systemd-analyze >/dev/null 2>&1; then
  if systemd-analyze calendar --iterations=3 "*-*-* 12:00:00 Asia/Colombo"; then
    echo "OK: systemd-analyze accepted the explicit-timezone calendar spec."
  else
    echo "WARNING: systemd-analyze rejected the explicit-timezone spec."
    echo "Fallback: drop the ' Asia/Colombo' suffix from OnCalendar= in"
    echo "anpia-daily.timer and instead set Environment=TZ=Asia/Colombo in"
    echo "anpia-daily.service, then re-run this check with:"
    echo '  systemd-analyze calendar --iterations=3 "*-*-* 12:00:00"'
  fi
else
  echo "systemd-analyze not available on this machine -- cannot verify the"
  echo "calendar spec locally. This is expected on a non-Linux development"
  echo "machine (e.g. this Windows session) -- verify on the actual target"
  echo "VM before enabling. AMBER, not a failure, per this task's own"
  echo "instructions."
fi

echo ""
echo "=== Unit file presence (informational only) ==="
if [ -f /etc/systemd/system/anpia-daily.service ] && [ -f /etc/systemd/system/anpia-daily.timer ]; then
  echo "Unit files ARE installed in /etc/systemd/system/."
  echo ""
  echo "=== systemctl status (read-only) ==="
  systemctl status anpia-daily.timer --no-pager 2>&1 || true
  echo ""
  echo "=== Next scheduled run (if enabled) ==="
  systemctl list-timers anpia-daily.timer --no-pager 2>&1 || true
else
  echo "Unit files are NOT installed. Nothing further to check on this host."
fi

echo ""
echo "=== Local unit file syntax check (source tree copies, not installed ones) ==="
if command -v systemd-analyze >/dev/null 2>&1; then
  systemd-analyze verify "$SCRIPT_DIR/systemd/anpia-daily.service" 2>&1 || echo "(verify reported issues above -- review before install; some warnings are expected for paths that only exist on the real target VM)"
else
  echo "systemd-analyze not available -- skipped (see note above)."
fi
