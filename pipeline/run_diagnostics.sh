#!/bin/zsh
# Run diagnostics with environment loaded from .env.local

cd "$(dirname "$0")/.."

# Check if .env.local exists
if [[ ! -f .env.local ]]; then
    echo "❌ .env.local not found"
    echo "   Create it from .env.example and add your credentials"
    exit 1
fi

# Load environment
set -a
source .env.local
set +a

# Run diagnostics
python3 pipeline/run_diagnostics.py
