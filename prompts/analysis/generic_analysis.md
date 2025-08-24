# Generic App Analysis Prompt

## Your Mission

Find all **real API endpoints** from this decompiled mobile application. This
prompt handles apps that don't fit standard categories or hybrid applications.

## Generic Analysis Strategy

### 1. Universal Search Patterns

Regardless of technology, search for:

- HTTP/HTTPS URLs in any text format
- Common API path patterns (`/api/`, `/v1/`, `/auth/`)
- Domain names that look like backends
- IP addresses with ports

### 2. File System Exploration

#### Search All Text Files

```bash
# Comprehensive URL search
find . -type f -exec grep -l "https\?://" {} \; 2>/dev/null

# Search for API patterns
find . -type f -exec grep -l "/api/\|/v[0-9]/\|auth" {} \; 2>/dev/null

# Look for configuration-like files
find . -name "*.json" -o -name "*.xml" -o -name "*.yml" -o -name "*.yaml" -o -name "*.conf" -o -name "*.config"
```

#### Binary File Analysis

```bash
# Extract strings from binary files
find . -type f -exec strings {} \; | grep -E "https?://" | sort -u

# Look for specific binary types
find . -name "*.so" -exec strings {} \; | grep -E "https?://"
find . -name "*.dll" -exec strings {} \; | grep -E "https?://"
```

### 3. Common Hybrid Frameworks

#### Cordova/PhoneGap

Look for:

- `assets/www/` directory with HTML/JavaScript
- `config.xml` with plugin configurations
- `cordova.js` or `phonegap.js`
- Plugin-specific configurations

#### Xamarin

Look for:

- Mono runtime files
- .NET assemblies in assets
- `assemblies/` directory
- Xamarin namespace references

#### Unity

Look for:

- `libunity.so` library
- Unity engine assets
- Asset bundles (`.unity3d` files)
- Unity configuration files

#### Titanium

Look for:

- Titanium runtime files
- JavaScript source in assets
- `tiapp.xml` configuration

#### Qt/QML

Look for:

- Qt runtime libraries
- QML source files
- Qt resource files (`.qrc`)

### 4. Web Technology Integration

#### WebView Applications

```bash
# Look for WebView-heavy apps
grep -r "WebView\|loadUrl\|webkit" .

# Check for embedded web content
find . -name "*.html" -o -name "*.htm" -o -name "*.js" -o -name "*.css"
```

#### Progressive Web Apps (PWA)

- Service worker files
- Web app manifests
- Cache configurations

### 5. Configuration Analysis

#### Standard Config Locations

```bash
# Android specific configs
cat AndroidManifest.xml | grep -E "https?://"

# Look for .properties files
find . -name "*.properties" -exec cat {} \;

# Environment files
find . -name ".env*" -exec cat {} \;

# INI-style configs
find . -name "*.ini" -exec cat {} \;
```

#### Asset-based Configuration

```bash
# Search all assets for URLs
find assets/ -type f -exec strings {} \; | grep -E "https?://" 2>/dev/null

# Resource files
find res/ -type f -exec strings {} \; | grep -E "https?://" 2>/dev/null
```

### 6. Obfuscation Detection & Handling

#### Base64 Encoding

```bash
# Look for Base64 patterns
grep -r "base64\|Base64\|decode" . | grep -v ".git"

# Common Base64 URL patterns
grep -r "[A-Za-z0-9+/=]\{20,\}" . | head -20
```

#### URL Building Patterns

```bash
# String concatenation patterns
grep -r "http\" + \|https\" + " .
grep -r "://\" + " .

# Template/format patterns
grep -r "%s://\|{}://" .
```

#### Encrypted/Encoded URLs

```bash
# Cryptographic patterns
grep -r "decrypt\|decode\|cipher\|crypt" . | grep -i url

# Hex patterns that might be URLs
grep -r "\\x[0-9a-fA-F]\{2\}" . | grep -E "(68 74 74 70|68747470)" # "http" in hex
```

### 7. Network Library Detection

#### Generic HTTP Libraries

```bash
# Look for common networking terms
grep -r -i "httpclient\|urlconnection\|okhttp\|retrofit\|volley" .

# Search for request/response patterns
grep -r -i "request\|response\|api.*call" .
```

#### Custom Network Code

```bash
# Socket programming
grep -r "Socket\|connect\|bind\|listen" .

# Low-level networking
grep -r "curl\|wget\|http.*get\|http.*post" .
```

### 8. Database and Storage Analysis

#### Local Databases

```bash
# SQLite databases
find . -name "*.db" -o -name "*.sqlite" -o -name "*.sqlite3"

# Check database schemas for URLs
sqlite3 database.db ".schema" | grep -i url
```

#### Key-Value Storage

```bash
# SharedPreferences (Android)
find . -name "*.xml" -path "*/shared_prefs/*"

# Plist files (iOS patterns in hybrid apps)
find . -name "*.plist"
```

## Analysis Priority for Unknown Apps

### Phase 1: Basic Discovery

1. **File type analysis**: What kind of files are present?
2. **Framework detection**: Any recognizable framework signatures?
3. **Manifest analysis**: What does AndroidManifest.xml reveal?
4. **Basic string extraction**: Simple grep for HTTP URLs

### Phase 2: Deep Analysis

1. **Binary analysis**: Extract strings from compiled files
2. **Configuration parsing**: Analyze all config files found
3. **Asset exploration**: Deep dive into assets directory
4. **Library identification**: What third-party libraries are used?

### Phase 3: Obfuscation Handling

1. **Encoding detection**: Look for Base64, hex, etc.
2. **String construction**: Find dynamically built URLs
3. **Encryption analysis**: Attempt to reverse simple encryption
4. **Native library analysis**: Check compiled libraries

## Expected Generic Artifacts

### Minimal Expected Findings

- At least basic HTTP/HTTPS URLs
- Configuration files with endpoints
- Third-party service URLs (analytics, ads, etc.)

### Comprehensive Analysis Results

- Complete API endpoint mapping
- Authentication flow URLs
- Third-party integration endpoints
- CDN and asset URLs
- Analytics and tracking URLs

## Output Format

```bash
# [ENDPOINT_NAME] - Found in [FILE_PATH:LINE] ([DETECTION_METHOD])
curl -X [METHOD] "[FULL_URL]" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer [TOKEN]"

# Example findings
# Main API - Found in assets/config.json (direct search)
curl -X GET "https://api.unknown-app.com/v1/data" \
  -H "Content-Type: application/json"

# Auth endpoint - Found in strings from libnetwork.so (binary analysis)
curl -X POST "https://auth.unknown-app.com/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass"}'

# Hidden endpoint - Found via Base64 decode of string in MainActivity.smali
curl -X GET "https://secret-api.unknown-app.com/internal" \
  -H "X-Secret-Key: [KEY]"
```

## Documentation Requirements

For each endpoint found:

1. **Discovery method**: How you found it (direct search, deobfuscation, etc.)
2. **File location**: Exact path and line number if applicable
3. **Context**: How the app appears to use this endpoint
4. **Confidence level**: High/Medium/Low based on evidence
5. **Deobfuscation process**: Step-by-step if URL was encoded/encrypted

## Success Criteria

1. **Comprehensive coverage**: Search every possible location
2. **Systematic approach**: Don't miss obvious hiding spots
3. **Deobfuscation attempts**: Try to decode any suspicious strings
4. **Documentation**: Clear trail of how each URL was found
5. **Verification**: Ensure URLs are complete and valid

Remember: Unknown apps might use any combination of technologies, so cast a wide
net and be thorough in your analysis.
