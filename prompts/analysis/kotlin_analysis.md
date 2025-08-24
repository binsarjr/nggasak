# Kotlin/Native Android Analysis Prompt

## Your Mission

Find all **real API endpoints** from this decompiled Kotlin/Android application.
Extract actual, working URLs that the app uses to communicate with servers.

## Analysis Strategy for Kotlin/Android Apps

### 1. Direct URL Search

Search through decompiled Java/Kotlin code for:

- HTTP/HTTPS URLs in string literals
- Retrofit interface definitions
- OkHttp client configurations
- HttpURLConnection usage
- WebView URL loading

### 2. String Analysis

Look in these locations:

- **Java source files**: Direct string declarations
- **strings.xml**: Resource string values
- **Smali files**: String constants in bytecode
- **Native libraries**: JNI string constants

### 3. Retrofit API Detection

Look for these patterns:

```java
@GET("/api/users")
@POST("/auth/login")
@PUT("/user/profile")
@DELETE("/user/{id}")
```

### 4. Network Client Configuration

Find network setup code:

```java
// OkHttp clients
OkHttpClient.Builder()
    .baseUrl("https://api.example.com")
    
// Retrofit instances
Retrofit.Builder()
    .baseUrl(BASE_URL)
```

### 5. Obfuscation Patterns in Android

#### Base64 Encoded URLs

```java
// Look for Base64.decode() calls
String decoded = new String(Base64.decode("aHR0cHM6Ly9hcGkuZXhhbXBsZS5jb20=", Base64.DEFAULT));
```

#### String Concatenation

```java
// URL building patterns
String baseUrl = "https://" + "api." + "example.com";
String endpoint = baseUrl + "/v1/users";
```

#### Encrypted URLs

```java
// Look for decrypt/decode methods
String url = CryptoUtils.decrypt(encryptedUrl);
String endpoint = StringUtils.decode(obfuscatedEndpoint);
```

#### Native Library URLs

```java
// JNI calls that return URLs
public native String getApiEndpoint();
public native String getBaseUrl();
```

### 6. Configuration and Constants

Check these files:

- `BuildConfig.java` - Build-time constants
- `Constants.java` - Application constants
- `Config.java` - Configuration classes
- `ApiEndpoints.java` - Endpoint definitions

### 7. Dynamic URL Construction

Look for patterns like:

```java
// Environment-based URLs
String baseUrl = BuildConfig.DEBUG ? "https://dev-api.com" : "https://api.com";

// User-specific URLs
String userEndpoint = String.format("%s/user/%d", BASE_URL, userId);

// Dynamic service discovery
String serviceUrl = getServiceUrl(serviceName);
```

## Search Commands for Analysis

### Grep Patterns

```bash
# Direct HTTP/HTTPS search
grep -r "https\?://" .

# API path patterns
grep -r "/api/" .
grep -r "/v[0-9]/" .

# Common endpoints
grep -r "login\|auth\|token" .
grep -r "user\|profile\|account" .

# Retrofit annotations
grep -r "@GET\|@POST\|@PUT\|@DELETE" .

# Base64 patterns
grep -r "Base64\." .
grep -r "decode\|decrypt" .
```

### File-specific searches

```bash
# In strings.xml files
find . -name "strings.xml" -exec grep -l "http" {} \;

# In Java source
find . -name "*.java" -exec grep -l "baseUrl\|BASE_URL" {} \;

# In Smali files
find . -name "*.smali" -exec grep -l "Ljava/lang/String;" {} \;
```

## Expected Output Format

For each endpoint found, provide:

```bash
# [ENDPOINT_NAME] - Found in [FILE_PATH] line [LINE_NUMBER]
curl -X [METHOD] "[FULL_URL]" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer [TOKEN]" \
  -d '[REQUEST_BODY_IF_POST]'

# Example authentication flow
curl -X POST "https://api.realapp.com/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'
```

## Documentation Requirements

For each found endpoint:

1. **Source Location**: Exact file and line number
2. **Deobfuscation Method**: How you decoded it (if obfuscated)
3. **Usage Context**: How the app uses this endpoint
4. **Parameters**: Expected request/response format
5. **Authentication**: Required headers or tokens

## Kotlin-Specific Considerations

### Coroutines and Suspend Functions

```kotlin
// Network calls in coroutines
suspend fun getUsers(): List<User> {
    return apiService.getUsers()
}
```

### Extension Functions

```kotlin
// URL building extensions
fun String.toApiUrl() = "https://api.com$this"
val endpoint = "/users".toApiUrl()
```

### Companion Objects

```kotlin
// Constants in companion objects
companion object {
    const val BASE_URL = "https://api.example.com"
    const val API_VERSION = "v1"
}
```

Your goal is to extract every possible real endpoint this Android app
communicates with, providing working curl commands for each one.
