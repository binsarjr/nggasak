# Flutter Analysis Prompt

## Your Mission

Find all **real API endpoints** from this decompiled Flutter application.
Flutter apps present unique challenges due to Dart compilation and asset
organization.

## Flutter-Specific Analysis Strategy

### 1. Asset-Based URL Discovery

Flutter stores configurations in assets:

- **flutter_assets/AssetManifest.json**: Asset registry
- **flutter_assets/FontManifest.json**: Font configurations
- **flutter_assets/packages/**: Package-specific assets
- **Custom config files**: JSON/YAML configuration files

### 2. Dart VM Snapshot Analysis

Flutter compiles Dart to native code:

- Look for VM snapshot files (`*_vm_snapshot*`)
- Search for string tables in snapshots
- Use specialized tools like `blutter` for analysis

### 3. String Extraction from Assets

```bash
# Extract all text from flutter_assets
find flutter_assets/ -type f -exec strings {} \; | grep -E "https?://"

# Check specific asset files
strings flutter_assets/AssetManifest.json | grep -E "https?://"
```

### 4. Configuration File Patterns

Flutter apps often use:

```dart
// Environment configurations
class ApiConfig {
  static const String baseUrl = "https://api.example.com";
  static const String apiVersion = "v1";
}

// Asset-based configs
final config = await rootBundle.loadString('assets/config.json');
```

### 5. HTTP Client Analysis

Look for Flutter HTTP patterns:

```dart
// Dio HTTP client
final dio = Dio();
dio.options.baseUrl = "https://api.example.com";

// http package
final response = await http.get(Uri.parse('https://api.example.com/users'));

// Custom HTTP clients
class ApiClient {
  static const String _baseUrl = "https://api.example.com";
}
```

### 6. Plugin Configuration

Check Flutter plugins that might contain URLs:

- `pubspec.yaml` references
- Plugin-specific configuration files
- Native plugin implementations

### 7. Obfuscation in Flutter

#### Asset-based Obfuscation

```dart
// URLs in asset files
final config = json.decode(await rootBundle.loadString('assets/secret.json'));
final apiUrl = config['api_url'];
```

#### Symbol Obfuscation

Flutter release builds obfuscate symbols:

- Look for hex-encoded strings
- Check for Base64 in asset files
- Search for encrypted configuration

#### Native Code URLs

Some URLs might be in native Android/iOS code:

- Check platform-specific implementations
- Look in native plugin code

## Analysis Commands

### Asset Extraction

```bash
# Extract Flutter assets from APK
unzip app.apk "flutter_assets/*"

# Search for URLs in all assets
grep -r "https\?://" flutter_assets/

# Look for API-related terms
grep -r -i "api\|endpoint\|server\|host" flutter_assets/
```

### Configuration Analysis

```bash
# Find JSON configuration files
find flutter_assets/ -name "*.json" -exec cat {} \;

# Look for YAML configs
find flutter_assets/ -name "*.yaml" -o -name "*.yml" -exec cat {} \;

# Search for environment configs
grep -r -i "prod\|dev\|staging\|base.*url" flutter_assets/
```

### Snapshot Analysis (Advanced)

```bash
# If using blutter tool
blutter app.apk output_dir

# Extract strings from native libraries
strings lib/arm64-v8a/libflutter.so | grep -E "https?://"
```

## Common Flutter URL Patterns

### Environment-based URLs

```dart
class Environment {
  static const bool isProduction = bool.fromEnvironment('PRODUCTION');
  static const String apiUrl = isProduction 
    ? 'https://api.production.com'
    : 'https://api.staging.com';
}
```

### Service Classes

```dart
class ApiService {
  static const String _baseUrl = 'https://api.example.com';
  static const String _apiVersion = 'v1';
  
  String get usersEndpoint => '$_baseUrl/$_apiVersion/users';
}
```

### Plugin Integration

```dart
// Firebase configuration
firebase_options.dart contains project URLs

// Social login plugins
google_sign_in: URLs in configuration

// Payment gateways
stripe/paypal: API endpoints in setup
```

## Expected Artifacts from Flutter Apps

### Configuration Files

- Environment-specific API URLs
- Feature flags and endpoints
- Third-party service configurations
- Analytics and tracking URLs

### Network Service Definitions

- HTTP client base URLs
- GraphQL endpoints
- WebSocket connections
- RESTful API definitions

### Asset-embedded URLs

- Image/media CDN URLs
- Documentation links
- Terms of service URLs
- Privacy policy links

## Output Format

```bash
# [ENDPOINT_NAME] - Found in [ASSET_FILE/LOCATION]
curl -X [METHOD] "[FULL_URL]" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer [TOKEN]"

# Example from asset configuration
# API Base URL - Found in flutter_assets/config.json
curl -X GET "https://api.flutterapp.com/v1/users" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: [API_KEY]"
```

## Flutter-Specific Challenges

1. **AOT Compilation**: Dart code compiled to native, not human-readable
2. **Asset Organization**: URLs scattered across multiple asset files
3. **Symbol Obfuscation**: Release builds obfuscate all symbols
4. **Plugin Dependencies**: URLs might be in third-party plugins
5. **Platform Channels**: Some endpoints might be in native code

## Analysis Priority

1. **Asset Files First**: Start with flutter_assets/ directory
2. **Configuration Discovery**: Look for JSON/YAML configs
3. **String Extraction**: Use strings command on all assets
4. **Native Analysis**: Check platform-specific code if needed
5. **Plugin Analysis**: Examine third-party plugin configurations

Remember: Flutter apps often hide URLs in asset files rather than compiled code,
so thorough asset analysis is crucial.
