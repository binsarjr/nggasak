# App Type Detection

## Task

Identify the technology stack of this Android app using your available tools to
explore the decompiled structure.

## App Types

- **Native Android** (Java/Kotlin)
- **Flutter**
- **React Native**
- **Xamarin**
- **Cordova/PhoneGap**
- **Unity**
- **Other/Hybrid**

## Key Indicators

- **Native**: `.smali` files, standard Android structure
- **Flutter**: `flutter_assets/` folder, `libflutter.so`
- **React Native**: JavaScript bundles, React signatures
- **Xamarin**: Mono runtime, .NET assemblies
- **Cordova**: `assets/www/` with HTML/JS
- **Unity**: `libunity.so`, Unity signatures

## Output Format

```
APP_TYPE: [Type]
CONFIDENCE: [High|Medium|Low]
EVIDENCE:
- Key evidence points

REASONING:
Brief explanation of classification.
```

Use your tools to systematically explore the structure and identify framework
signatures.
