# Android App Endpoint Analysis

## Task

Find all real API endpoints from this Android app. Focus on actual HTTP/HTTPS
URLs.

## Search Strategy

1. **Direct URLs**: Look for `http://` and `https://` strings
2. **Retrofit APIs**: Find `@GET`, `@POST`, `@PUT`, `@DELETE` annotations
3. **Base URLs**: Search for `baseUrl`, `BASE_URL`, `API_URL` variables
4. **Obfuscated URLs**: Check for Base64 encoded strings and string
   concatenation

## Common Locations

- Java/Kotlin source files
- `strings.xml` resource files
- `AndroidManifest.xml`
- Configuration classes
- Network client setup code

## Required Output

For each endpoint found, provide:

```bash
# [Description] - Found in [file:line]
curl -X [METHOD] "[URL]" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer [TOKEN]"
```

Analyze the provided files and extract all discoverable endpoints.
