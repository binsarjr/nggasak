#!/bin/bash

# Auto-detect JAVA_HOME
export JAVA_HOME=$(dirname $(dirname $(readlink -f $(which java))))

echo "=================================================================="
echo "🔍 Nggasak Analysis Tools Container"
echo "=================================================================="
echo ""
echo "🛠️  Available Reverse Engineering Tools:"
echo "   • apktool      - $(apktool --version 2>&1 | head -1 || echo 'APK decompiler/recompiler')"
echo "   • dex2jar      - DEX to JAR converter (d2j-dex2jar)"
echo "   • jadx         - $(jadx --version 2>&1 | head -1 || echo 'Java decompiler for Android')"
echo "   • reflutter    - $(reflutter --version 2>&1 | head -1 || echo 'Flutter app analysis tool')"
echo "   • claude       - $(claude --version 2>&1 | head -1 || echo 'Claude Code CLI - AI-powered analysis')"
echo ""
echo "🤖 AI-Powered Analysis Examples:"
echo "   claude --dangerously-skip-permissions \"analyze this decompiled APK structure\""
echo "   claude --dangerously-skip-permissions \"find encryption patterns in Java code\""
echo "   claude --dangerously-skip-permissions \"identify security vulnerabilities\""
echo ""
echo "📂 Working Directory: /data"
echo "📁 Analysis Output: /analysis"
echo ""
echo "🔐 Environment Configuration:"
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "   ⚠️  ANTHROPIC_API_KEY not set - Claude Code won't work"
    echo "   💡 Set it in .env file: ANTHROPIC_API_KEY=\"your_key\""
else
    echo "   ✅ ANTHROPIC_API_KEY is configured"
fi

# Show base URL if customized
if [ -n "$ANTHROPIC_BASE_URL" ]; then
    echo "   🌐 ANTHROPIC_BASE_URL: $ANTHROPIC_BASE_URL"
else
    echo "   🌐 ANTHROPIC_BASE_URL: https://api.anthropic.com (default)"
fi

# Show other environment variables if set
if [ -n "$DEBUG" ]; then
    echo "   🐛 DEBUG mode: $DEBUG"
fi

if [ -n "$JAVA_OPTS" ]; then
    echo "   ☕ JAVA_OPTS: $JAVA_OPTS"
    export JAVA_OPTS
fi

if [ -n "$LOG_LEVEL" ]; then
    echo "   📝 LOG_LEVEL: $LOG_LEVEL"
fi
echo ""
echo "🚀 Quick Start Workflow:"
echo "   1. apktool d app.apk -o decompiled/"
echo "   2. claude --dangerously-skip-permissions \"analyze the decompiled APK\""
echo "   3. jadx app.apk -d jadx_output/"
echo "   4. claude --dangerously-skip-permissions \"find APIs in Java code\""
echo ""
echo "=================================================================="
echo ""

# Execute the command or start bash
if [ "$#" -eq 0 ]; then
    exec /bin/bash
else
    exec "$@"
fi
