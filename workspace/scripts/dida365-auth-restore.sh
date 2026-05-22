#!/bin/bash
# Dida365 CLI Authentication Restore Script
# This script restores dida365-cli authentication from saved environment variables

set -e

# Source the global environment file
if [ -f "/home/node/.openclaw/workspace/.env" ]; then
    source "/home/node/.openclaw/workspace/.env"
fi

# Check if token exists
if [ -z "$DIDA365_COOKIE_TOKEN" ]; then
    echo "Error: DIDA365_COOKIE_TOKEN not found in environment"
    exit 1
fi

# Change to dida365-cli directory
cd "/home/node/.openclaw/workspace/skills/dida365-cli"

# Restore authentication
echo "Restoring dida365-cli authentication..."
npx dida365 auth cookie "$DIDA365_COOKIE_TOKEN"

# Verify authentication
echo "Verifying authentication..."
npx dida365 auth status

echo "✅ Dida365 CLI authentication restored successfully!"