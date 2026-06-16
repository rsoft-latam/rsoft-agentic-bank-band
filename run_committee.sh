#!/usr/bin/env bash
# Launch all 6 Loan Committee peers (each keeps a WS connection to Band).
cd "$(dirname "$0")"
# Arranque escalonado: 6 conexiones WS simultáneas provocan reconnect-storm
for name in BankGatekeeper BankAnalyst BankCFO BankSettler BankAuditor BorrowerClient1; do
  .venv/bin/python -m committee.peer "$name" &
  sleep 4
done
trap 'kill 0' SIGINT SIGTERM
wait
