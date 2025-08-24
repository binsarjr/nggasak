#!/usr/bin/env bash
# Minimal Claude CLI wrapper using Anthropic Python SDK.
# Usage:
#   claude "your prompt here"
#   claude --dangerously-skip-permissions "your prompt here"

set -euo pipefail

# Accept an optional flag and then the prompt
PROMPT=""
for arg in "$@"; do
  if [[ "$arg" != --dangerously-skip-permissions ]]; then
    if [[ -z "$PROMPT" ]]; then
      PROMPT="$arg"
    else
      PROMPT="$PROMPT $arg"
    fi
  fi
done

if [[ -z "${PROMPT}" ]]; then
  echo "Usage: claude [--dangerously-skip-permissions] \"prompt\"" >&2
  exit 2
fi

# Map ANTHROPIC_AUTH_TOKEN -> ANTHROPIC_API_KEY if needed
if [[ -n "${ANTHROPIC_AUTH_TOKEN:-}" && -z "${ANTHROPIC_API_KEY:-}" ]]; then
  export ANTHROPIC_API_KEY="$ANTHROPIC_AUTH_TOKEN"
fi

python3 - "$PROMPT" <<'PY'
import os
import sys
from anthropic import Anthropic

prompt = sys.argv[1]
api_key = os.getenv("ANTHROPIC_API_KEY")
base_url = os.getenv("ANTHROPIC_BASE_URL")

if not api_key:
    print("[claude-wrapper] ANTHROPIC_API_KEY not set", file=sys.stderr)
    sys.exit(3)

client = Anthropic(api_key=api_key, base_url=base_url) if base_url else Anthropic(api_key=api_key)

# Keep output simple text
msg = client.messages.create(
    model=os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20240620"),
    max_tokens=1500,
    messages=[{"role": "user", "content": prompt}],
)

# Messages API returns a list of content blocks; print text parts
for block in msg.content:
    if block.type == "text":
        print(block.text)
PY
