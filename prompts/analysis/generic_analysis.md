# Generic App Endpoint Analysis

## Task

Find all real API endpoints from this mobile app. Use universal search patterns
for unknown app types.

## Universal Search Strategy

1. **Text Search**: Look for `http://` and `https://` in all files
2. **API Patterns**: Search for `/api/`, `/v1/`, `/auth/` paths
3. **Configuration Files**: Check `.json`, `.xml`, `.yml`, `.conf` files
4. **String Extraction**: Use `strings` command on binary files

## Key Commands

```bash
# Find HTTP URLs in all files
find . -type f -exec grep -l "https\?://" {} \;

# Search for API patterns
grep -r "/api/\|/v[0-9]/\|auth" .

# Extract strings from binaries
find . -name "*.so" -exec strings {} \; | grep -E "https?://"
```

## Look For

- Configuration files with endpoints
- String resources with URLs
- WebView content
- Network client setup
- Base64 encoded URLs

## Required Output

```bash
# [Description] - Found in [file]
curl -X [METHOD] "[URL]" \
  -H "Content-Type: application/json"
```

Use comprehensive file scanning since app type is unknown.
