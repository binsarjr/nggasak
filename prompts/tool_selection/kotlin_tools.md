# Kotlin/Native Android Analysis Tools

## Recommended Tool Chain

### 1. Primary Decompilation

- **jadx**: Best for readable Java/Kotlin code
- **apktool**: Essential for resources and smali analysis
- **dex2jar + jd-gui**: Backup decompilation method

### 2. Static Analysis Tools

- **jadx-gui**: Interactive exploration
- **smali/baksmali**: Smali code manipulation
- **aapt/aapt2**: Resource analysis
- **strings**: Extract hardcoded strings

### 3. Dynamic Analysis Tools

- **frida**: Runtime manipulation and hooking
- **xposed**: Framework modification (if applicable)
- **objection**: Mobile runtime exploration

### 4. Specialized Tools

- **apkanalyzer**: Android Studio tool for deep APK inspection
- **classyshark**: APK browser and analyzer
- **MobSF**: Comprehensive mobile security framework

## Analysis Priority

### Phase 1: Basic Structure

1. Use `jadx` for main code analysis
2. Use `apktool` for resources and manifest
3. Extract strings with `strings` command

### Phase 2: Security Analysis

1. Look for hardcoded credentials
2. Analyze network security config
3. Check for certificate pinning
4. Review permissions and components

### Phase 3: Dynamic Behavior

1. Use `frida` for runtime analysis
2. Monitor network traffic
3. Hook security-sensitive functions

## Tool Commands

### JADX Analysis

```bash
jadx -d output_dir app.apk
jadx-gui app.apk  # Interactive mode
```

### APKTool Analysis

```bash
apktool d app.apk -o decompiled/
apktool if framework-res.apk  # If needed
```

### String Extraction

```bash
strings app.apk | grep -E "(http|api|key|token|password)"
```

### Frida Hooking Examples

```javascript
// Hook specific methods
Java.perform(function () {
  var MainActivity = Java.use("com.example.MainActivity");
  MainActivity.sensitiveMethod.implementation = function () {
    console.log("Hooked sensitive method");
    return this.sensitiveMethod();
  };
});
```

## Expected Artifacts

- Decompiled Java/Kotlin source code
- Android resources and layouts
- Manifest with permissions and components
- Native libraries (if present)
- Obfuscated code patterns
- Security configurations
