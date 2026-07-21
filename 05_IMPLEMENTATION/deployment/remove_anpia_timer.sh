#!/usr/bin/env bash
# remove_anpia_timer.sh -- REQ-ANPIA-REQ-01-D02
#
# NOT RUN AS PART OF THIS TASK. Cleanly disables, stops, and removes the
# ANPIA timer/service unit files. Safe to run even if the timer was never
# installed or enabled (each step is best-effort / idempotent).

set -uo pipefail

SYSTEMD_DIR="/etc/systemd/system"

if [ "$(id -u)" -ne 0 ]; then
  echo "This script must be run with sudo/root." >&2
  exit 1
fi

echo "Stopping and disabling anpia-daily.timer (if active)..."
systemctl disable --now anpia-daily.timer 2>/dev/null || true

echo "Removing unit files from $SYSTEMD_DIR..."
rm -f "$SYSTEMD_DIR/anpia-daily.service" "$SYSTEMD_DIR/anpia-daily.timer"

systemctl daemon-reload
systemctl reset-failed anpia-daily.service anpia-daily.timer 2>/dev/null || true

echo "Removed. Confirm with: systemctl list-timers | grep anpia"
