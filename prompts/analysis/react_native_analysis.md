# React Native Endpoint Analysis

## Task

Find all real API endpoints from this React Native app by analyzing JavaScript
bundles.

## Key Locations

- `assets/index.android.bundle` - Main JavaScript bundle
- `assets/*.bundle` - Split bundles
- Look for beautified or decompiled JS code

## Search Patterns

1. **API Calls**: `fetch(`, `axios.`, `http.get`, `api.`
2. **Base URLs**: `baseURL`, `apiUrl`, `BASE_URL`
3. **Environment URLs**: `__DEV__`, `process.env`
4. **String Concatenation**: URL building patterns

## Common Patterns

```javascript
fetch("https://api.example.com/users");
axios.defaults.baseURL = "https://api.example.com";
const API_URL = "https://api.example.com";
```

## Required Output

```bash
# [Description] - Found in [bundle file]
curl -X [METHOD] "[URL]" \
  -H "Content-Type: application/json"
```

Focus on extracting the JavaScript bundle first, then search for HTTP/HTTPS
patterns.
