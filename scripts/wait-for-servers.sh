#!/bin/bash
set -e

# Wait for LangPlug servers to be ready
# Usage: ./scripts/wait-for-servers.sh [timeout_seconds]

BACKEND_READINESS_URL="http://localhost:8000/readiness"
FRONTEND_URL="http://localhost:3000"
TIMEOUT=${1:-120}  # Default 120 seconds (AI models can take time)
CHECK_INTERVAL=2

echo "============================================================"
echo "          Waiting for LangPlug Servers"
echo "============================================================"
echo ""
echo "Backend:  $BACKEND_READINESS_URL"
echo "Frontend: $FRONTEND_URL"
echo "Timeout:  ${TIMEOUT}s (checking every ${CHECK_INTERVAL}s)"
echo ""

elapsed=0
backend_ready=false
frontend_ready=false
backend_message=""

while [ $elapsed -lt $TIMEOUT ]; do
    # Check backend readiness endpoint
    if ! $backend_ready; then
        response=$(curl -s -w "\n%{http_code}" -m 2 "$BACKEND_READINESS_URL" 2>/dev/null || echo -e "\n000")
        http_code=$(echo "$response" | tail -1)
        body=$(echo "$response" | sed '$d')

        if [ "$http_code" = "200" ]; then
            # Backend is ready
            backend_message=$(echo "$body" | grep -o '"message":"[^"]*"' | cut -d'"' -f4 || echo "Ready")
            echo "[$(printf '%3d' $elapsed)s] Backend: $backend_message"
            backend_ready=true
        elif [ "$http_code" = "503" ]; then
            # Backend is starting (503 Service Unavailable with message)
            backend_message=$(echo "$body" | grep -o '"message":"[^"]*"' | cut -d'"' -f4 || echo "Initializing...")
            if [ $((elapsed % 10)) -eq 0 ] || [ $elapsed -eq 2 ]; then
                echo "[$(printf '%3d' $elapsed)s] Backend: $backend_message"
            fi
        else
            # Backend not responding yet
            if [ $((elapsed % 10)) -eq 0 ] || [ $elapsed -eq 2 ]; then
                echo "[$(printf '%3d' $elapsed)s] Backend: Waiting for server to start..."
            fi
        fi
    fi

    # Check frontend
    if ! $frontend_ready; then
        if curl -s -f -m 2 "$FRONTEND_URL" > /dev/null 2>&1; then
            echo "[$(printf '%3d' $elapsed)s] Frontend: Ready"
            frontend_ready=true
        fi
    fi

    # Exit if both are ready
    if $backend_ready && $frontend_ready; then
        echo ""
        echo "============================================================"
        echo "[SUCCESS] All servers are ready!"
        echo "============================================================"
        echo ""
        echo "Backend:  http://localhost:8000"
        echo "          - API Docs: http://localhost:8000/docs"
        echo "          - Health:   http://localhost:8000/health"
        echo ""
        echo "Frontend: http://localhost:3000"
        exit 0
    fi

    sleep $CHECK_INTERVAL
    elapsed=$((elapsed + CHECK_INTERVAL))
done

# Timeout reached
echo ""
echo "============================================================"
echo "[TIMEOUT] Servers did not become ready within ${TIMEOUT}s"
echo "============================================================"
echo ""

if ! $backend_ready; then
    echo "[FAIL] Backend is NOT responding at $BACKEND_READINESS_URL"
fi

if ! $frontend_ready; then
    echo "[FAIL] Frontend is NOT responding at $FRONTEND_URL"
fi

echo ""
echo "Check the Backend Server and Frontend Server windows for errors."
exit 1
