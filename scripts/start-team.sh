#!/bin/bash
cd "$(dirname "$0")/.."

while true; do
    echo "[$(date)] Starting team-agent..."
    python -m kiro_multi_agent team start

    if [ -f "restart.flag" ]; then
        rm -f "restart.flag"
        echo "[$(date)] Restart requested, restarting in 3s..."
        sleep 3
    else
        echo "[$(date)] Exited without restart flag. Stopping."
        break
    fi
done
