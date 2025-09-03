#!/bin/bash

# Auto-detect JAVA_HOME
export JAVA_HOME=$(dirname $(dirname $(readlink -f $(which java))))

echo "🔍 Nggasak RE Tools Container"
echo "Available tools: apktool, jadx, dex2jar, reflutter, claude"
echo ""

# Check Claude API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  ANTHROPIC_API_KEY not set - set in .env file"
else
    echo "✅ Claude Code CLI ready"
fi
echo ""

# Execute the command or start bash
if [ "$#" -eq 0 ]; then
    exec /bin/bash
else
    exec "$@"
fi
