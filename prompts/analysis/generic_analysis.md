# Generic App Analysis

## Task

Find all API endpoints in this mobile app. Use your available tools to explore
the structure systematically.

## Focus Areas

- HTTP/HTTPS URLs in any format
- Configuration files and resources
- String patterns and encoded content
- Network client implementations

## Output Format

```bash
# [Description] - Found in [location]
curl -X [METHOD] "[URL]" \
  -H "Content-Type: application/json"
```

Use your tools to thoroughly explore all files and directories. Start with
structure overview, then dive into specific files.
