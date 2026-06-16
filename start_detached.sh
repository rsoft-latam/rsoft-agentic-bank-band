#!/usr/bin/env bash
# Launch the 6 peers FULLY DETACHED (nohup) so they survive after this
# launcher exits — avoids the process-group kill when a background task is
# reaped. Each peer logs to logs/<name>.log. Staggered to avoid WS storm.
cd "$(dirname "$0")"
mkdir -p logs
for name in BankGatekeeper BankAnalyst BankCFO BankSettler BankAuditor BorrowerClient1; do
  nohup .venv/bin/python -m committee.peer "$name" > "logs/$name.log" 2>&1 &
  disown
  sleep 4
done
echo "6 peers lanzados detached. Logs en logs/. PIDs:"
pgrep -f "committee.peer" | tr '\n' ' '; echo
