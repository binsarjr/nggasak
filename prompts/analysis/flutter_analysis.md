# Flutter Endpoint Analysis

## Task

Find all real API endpoints from this Flutter app by analyzing assets and
configurations.

## Key Locations

- `flutter_assets/` directory
- `flutter_assets/AssetManifest.json`
- Configuration JSON/YAML files in assets
- `lib/` directories for native code

## Search Strategy

1. **Asset Files**: Search all files in `flutter_assets/` for HTTP URLs
2. **Configuration**: Check JSON/YAML files for API configurations
3. **String Extraction**: Use `strings` command on asset files
4. **Native Bridge**: Check platform-specific implementations

## Common Patterns

```dart
static const String baseUrl = "https://api.example.com";
final config = json.decode(await rootBundle.loadString('assets/config.json'));
```

## Analysis Commands

```bash
# Search for URLs in assets
find flutter_assets/ -type f -exec strings {} \; | grep -E "https?://"

# Check configuration files
find flutter_assets/ -name "*.json" -exec cat {} \;
```

## Required Output

```bash
# [Description] - Found in [asset file]
curl -X [METHOD] "[URL]" \
  -H "Content-Type: application/json"
```

Focus on asset files since Flutter compiles Dart code to native bytecode.
