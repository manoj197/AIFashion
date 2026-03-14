#!/bin/bash
# ─────────────────────────────────────────────────
# Fashion AI — Local Pipeline Runner
# ─────────────────────────────────────────────────
# Run this locally instead of waiting for GitHub Actions.
# 
# Usage:
#   ./scripts/run_local.sh
#
# Requirements:
#   - Python 3.10+
#   - ANTHROPIC_API_KEY environment variable set
# ─────────────────────────────────────────────────

set -e

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ Error: ANTHROPIC_API_KEY is not set."
    echo ""
    echo "Set it with:"
    echo "  export ANTHROPIC_API_KEY=sk-ant-..."
    echo ""
    exit 1
fi

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed."
    exit 1
fi

# Check for anthropic package
python3 -c "import anthropic" 2>/dev/null || {
    echo "📦 Installing anthropic SDK..."
    pip install anthropic
}

echo ""
echo "🏢 Fashion AI — Running Agent Pipeline Locally"
echo "================================================"
echo ""

# Run the orchestrator
python3 scripts/orchestrator.py

echo ""
echo "📁 Changes made to your local files."
echo "Review them, then commit and push when ready."
echo ""
