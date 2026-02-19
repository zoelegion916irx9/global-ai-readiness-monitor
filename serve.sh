#!/bin/bash

# MENA AI Readiness Monitor - Local Development Server
#
# This script starts a simple HTTP server to serve the dashboard locally.
# The server is needed because the dashboard loads data.json via fetch(),
# which requires an HTTP server due to browser CORS restrictions.

PORT=${1:-8000}

echo "=================================================="
echo "  MENA AI Readiness Monitor - Local Server"
echo "=================================================="
echo ""
echo "Starting server on http://localhost:$PORT"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Try Python 3 first, then Python 2
if command -v python3 &> /dev/null; then
    python3 -m http.server $PORT
elif command -v python &> /dev/null; then
    python -m SimpleHTTPServer $PORT
else
    echo "Error: Python is not installed."
    echo ""
    echo "Alternative options:"
    echo "  - Install Python 3"
    echo "  - Use 'npx http-server -p $PORT' (requires Node.js)"
    echo "  - Use 'php -S localhost:$PORT' (requires PHP)"
    exit 1
fi
