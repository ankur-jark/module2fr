#!/bin/bash

# Stop development services

echo "Stopping TruScholar services..."

# Stop services using PID files
if [ -d "logs" ]; then
    for pidfile in logs/*.pid; do
        if [ -f "$pidfile" ]; then
            pid=$(cat "$pidfile")
            if ps -p $pid > /dev/null; then
                kill $pid
                echo "Stopped process $pid"
            fi
            rm "$pidfile"
        fi
    done
fi

echo "All services stopped."