# Flutter Analysis Tools

## Recommended Tool Chain

### 1. Flutter-Specific Tools

- **flutter_tools**: Official Flutter toolkit
- **reFlutter**: Flutter app patching and analysis
- **blutter**: Flutter bytecode analysis
- **darter**: Dart snapshot analysis

### 2. Dart Analysis

- **dart**: Official Dart compiler and analyzer
- **dartfmt**: Code formatting (for readable analysis)
- **dart2js**: Dart to JavaScript compiler (reverse analysis)

### 3. Generic Mobile Tools

- **jadx**: For Android wrapper code
- **apktool**: For resources and manifest
- **class-dump**: For iOS Flutter apps

### 4. Specialized Flutter Tools

- **Doldrums**: Flutter reverse engineering toolkit
- **flutter_engine_tracer**: Engine-level analysis
- **snapshot_analyzer**: Dart VM snapshot inspector

## Analysis Priority

### Phase 1: Flutter Detection

1. Confirm Flutter signature in assets
2. Locate `flutter_assets/` directory
3. Find Dart VM snapshots
4. Identify Flutter engine version

### Phase 2: Asset Extraction

1. Extract Flutter assets
2. Analyze asset manifest
3. Decode images and fonts
4. Extract localization files

### Phase 3: Code Analysis

1. Analyze Dart snapshots
2. Extract widget trees
3. Find business logic
4. Identify network calls

## Tool Commands

### reFlutter Setup

```bash
python reFlutter.py app.apk
# Generates patched APK for dynamic analysis
```

### Blutter Analysis

```bash
blutter app.apk output_dir
# Extracts and analyzes Dart bytecode
```

### Asset Extraction

```bash
# Extract flutter_assets
unzip app.apk flutter_assets/*
# Analyze asset manifest
cat flutter_assets/AssetManifest.json
```

### Snapshot Analysis

```bash
# Find VM snapshots
find . -name "*_vm_snapshot*"
# Analyze with custom tools
snapshot_analyzer vm_snapshot_data
```

## Expected Artifacts

- Flutter assets and resources
- Dart VM snapshots
- Widget composition trees
- Network service definitions
- Plugin configurations
- Platform channel implementations

## Flutter-Specific Challenges

- Compiled Dart code (not human-readable)
- Obfuscated symbol names
- AOT compilation artifacts
- Platform channel bridging code
- Engine-level optimizations

## Dynamic Analysis Approach

1. Use reFlutter for runtime patching
2. Hook Flutter engine calls
3. Monitor platform channel communication
4. Trace widget lifecycle events
