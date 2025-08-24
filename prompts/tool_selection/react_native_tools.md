# React Native Analysis Tools

## Recommended Tool Chain

### 1. JavaScript Analysis Tools

- **metro-symbolicate**: React Native bundle analysis
- **react-native-decompiler**: Bundle decompilation
- **hermes-dec**: Hermes bytecode decompiler
- **js-beautify**: JavaScript formatting and cleanup

### 2. Bundle Analysis

- **webpack-bundle-analyzer**: Bundle composition analysis
- **source-map-explorer**: Source map analysis
- **metro-bundler**: Bundle inspection tools
- **jscodeshift**: Code transformation and analysis

### 3. Native Bridge Analysis

- **jadx**: For Android native modules
- **class-dump**: For iOS native modules
- **nm**: Symbol analysis for native libraries
- **objdump**: Disassembly of native code

### 4. Runtime Analysis

- **flipper**: React Native debugging platform
- **reactotron**: Development and debugging tool
- **frida**: Runtime hooking and manipulation

## Analysis Priority

### Phase 1: Bundle Identification

1. Locate JavaScript bundles
2. Identify bundle format (Metro, Webpack, etc.)
3. Check for Hermes bytecode
4. Find source maps (if available)

### Phase 2: Bundle Decompilation

1. Extract JavaScript code
2. Deobfuscate minified code
3. Reconstruct component hierarchy
4. Identify API endpoints

### Phase 3: Native Module Analysis

1. Analyze native Android/iOS components
2. Examine bridge implementations
3. Review native module interfaces
4. Check for custom native code

## Tool Commands

### Bundle Extraction

```bash
# Extract from APK
unzip app.apk assets/index.android.bundle
# Or look for other bundle names
find . -name "*.bundle" -o -name "*.jsbundle"
```

### Hermes Decompilation

```bash
# If Hermes bytecode is used
hermes-dec index.android.bundle -o decompiled/
```

### JavaScript Beautification

```bash
# Make minified code readable
js-beautify index.android.bundle > readable.js
```

### Source Map Analysis

```bash
# If source maps exist
source-map-explorer bundle.js bundle.js.map
```

### Bundle Analysis

```bash
# Analyze bundle composition
npx @react-native-community/cli bundle-analyzer
```

## Expected Artifacts

- JavaScript bundle files
- React component definitions
- Redux/state management code
- API service definitions
- Navigation structures
- Native module interfaces

## React Native Specific Challenges

- Minified/obfuscated JavaScript
- Hermes bytecode compilation
- Bridge communication patterns
- Native module integration
- Metro bundler optimizations

## Dynamic Analysis Approach

1. Use Flipper for runtime inspection
2. Hook React Native bridge calls
3. Monitor network requests
4. Trace component lifecycle
5. Analyze state management patterns

## Common File Locations

```
assets/index.android.bundle    # Main JavaScript bundle
assets/index.android.bundle.map # Source map (if present)
lib/*/libreactnativejni.so    # React Native JNI
lib/*/libhermes.so            # Hermes runtime (if used)
```
