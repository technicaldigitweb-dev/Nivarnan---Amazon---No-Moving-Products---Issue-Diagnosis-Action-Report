#!/usr/bin/env bash
# install_anpia_timer.sh -- REQ-ANPIA-REQ-01-D02
#
# NOT RUN AS PART OF THIS TASK. Provided for a future deployment operator to
# run manually on the target Linux VM, after reviewing every path/user/
# environment placeholder in anpia-daily.service. This script requires
# explicit confirmation and root/sudo -- it will refuse to run silently.
#
# What it does when actually run:
#   1. Copies anpia-daily.service and anpia-daily.timer into
#      /etc/systemd/system/
#   2. Runs `systemctl daemon-reload`
#   3. Does NOT enable or start the timer -- that is a separate, explicit
#      step the operator must take deliberately (`systemctl enable --now
#      anpia-daily.timer`), intentionally left out of this script so that
#      copying the unit files can never accidentally activate the schedule.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYSTEMD_DIR="/etc/systemd/system"

if [ "$(id -u)" -ne 0 ]; then
  echo "This script must be run with sudo/root -- it writes to $SYSTEMD_DIR." >&2
  exit 1
fi

echo "This will copy the following unit files into $SYSTEMD_DIR:"
echo "  - anpia-daily.service"
echo "  - anpia-daily.timer"
echo "It will NOT enable or start the timer. Review the unit files first --"
echo "in particular User=, Group=, WorkingDirectory=, EnvironmentFile=, and"
echo "the ANPIA_PROJECT_ROOT / ANPIA_PYTHON_BIN / ANPIA_ENV_FILE values --"
echo "the shipped placeholders (/opt/anpia, anpia-svc, /etc/anpia/...) are"
echo "examples, not guaranteed-correct values for this VM."
read -r -p "Type INSTALL to proceed: " CONFIRM
if [ "$CONFIRM" != "INSTALL" ]; then
  echo "Aborted -- confirmation phrase did not match."
  exit 1
fi

cp "$SCRIPT_DIR/systemd/anpia-daily.service" "$SYSTEMD_DIR/anpia-daily.service"
cp "$SCRIPT_DIR/systemd/anpia-daily.timer" "$SYSTEMD_DIR/anpia-daily.timer"
systemctl daemon-reload

echo ""
echo "Unit files installed. The timer is NOT enabled or started."
echo "To activate (only after verifying the schedule with check_anpia_timer.sh):"
echo "  sudo systemctl enable --now anpia-daily.timer"
