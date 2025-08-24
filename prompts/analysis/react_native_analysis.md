# React Native Analysis Prompt

## Your Mission

Find all **real API endpoints** from this decompiled React Native application.
React Native apps contain JavaScript bundles that need special handling.

## React Native Analysis Strategy

### 1. JavaScript Bundle Location

React Native bundles are typically found in:

- `assets/index.android.bundle` (Android)
- `main.jsbundle` (iOS)
- `assets/index.bundle` (Alternative naming)
- Split bundles in separate files

### 2. Bundle Analysis Approach

#### Bundle Extraction

```bash
# Extract JavaScript bundle from APK
unzip app.apk assets/index.android.bundle

# Check for multiple bundles
find . -name "*.bundle" -o -name "*.jsbundle"
```

#### Bundle Decompilation

```bash
# Make minified code readable
js-beautify index.android.bundle > readable.js

# If using Hermes bytecode
hermes-dec index.android.bundle -o decompiled_js/
```

### 3. Common React Native URL Patterns

#### Fetch/Axios API Calls

```javascript
// Direct fetch calls
fetch("https://api.example.com/users");

// Axios configurations
axios.defaults.baseURL = "https://api.example.com";

// Service classes
class ApiService {
  constructor() {
    this.baseURL = "https://api.example.com";
  }
}
```

#### Environment Configuration

```javascript
// Environment-based URLs
const API_URL = __DEV__
  ? "https://dev-api.example.com"
  : "https://api.example.com";

// Config objects
const config = {
  development: "https://dev-api.com",
  production: "https://api.com",
};
```

#### Redux/State Management

```javascript
// Redux actions with API calls
const fetchUsers = () => (dispatch) => {
  return fetch("https://api.example.com/users")
    .then((response) => response.json())
    .then((data) => dispatch(setUsers(data)));
};

// Saga effects
function* fetchUserSaga() {
  const response = yield call(fetch, "https://api.example.com/user");
}
```

### 4. Obfuscation Patterns in React Native

#### String Obfuscation

```javascript
// Base64 encoded URLs
const apiUrl = atob('aHR0cHM6Ly9hcGkuZXhhbXBsZS5jb20=');

// Character array construction
const url = ['h','t','t','p','s',':','/','/','a','p','i','.','c','o','m'].join('');

// Hex encoding
const endpoint = String.fromCharCode(0x68, 0x74, 0x74, 0x70, 0x73, ...);
```

#### Environment Variables

```javascript
// Process environment (Metro bundler)
const API_URL = process.env.REACT_NATIVE_API_URL;

// Build-time constants
const Config = {
  API_URL: __API_URL__, // Replaced at build time
};
```

#### Dynamic URL Construction

```javascript
// Template literals
const apiUrl = `https://${subdomain}.example.com/${version}`;

// Function-based construction
function getApiUrl(environment) {
  return `https://api-${environment}.example.com`;
}
```

### 5. Network Library Detection

#### Popular Libraries

- **axios**: HTTP client library
- **fetch**: Native JavaScript fetch API
- **superagent**: HTTP request library
- **apollo-client**: GraphQL client
- **relay**: Facebook's GraphQL client

#### Library-specific Patterns

```javascript
// Apollo GraphQL
const client = new ApolloClient({
  uri: "https://api.example.com/graphql",
});

// React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      queryFn: ({ queryKey }) =>
        fetch(`https://api.example.com/${queryKey[0]}`),
    },
  },
});
```

### 6. Navigation and Deep Links

```javascript
// Deep link URLs
const linking = {
  prefixes: ["https://myapp.com", "myapp://"],
  config: {
    screens: {
      Profile: "profile/:id",
    },
  },
};

// WebView URLs
<WebView source={{ uri: "https://example.com/terms" }} />;
```

## Analysis Commands

### Bundle Search Patterns

```bash
# Extract and search for URLs
strings index.android.bundle | grep -E "https?://"

# Search for API patterns
grep -o "https\?://[^\"'\s]*" readable.js

# Look for common API terms
grep -i "api\|endpoint\|baseurl\|server" readable.js

# Search for authentication endpoints
grep -i "login\|auth\|token\|oauth" readable.js
```

### Network Code Patterns

```bash
# Fetch calls
grep -n "fetch(" readable.js

# Axios patterns
grep -n "axios\." readable.js

# WebSocket connections
grep -n "WebSocket\|ws://" readable.js

# GraphQL endpoints
grep -n "graphql\|apollo" readable.js
```

## Source Map Analysis (If Available)

```bash
# Look for source maps
find . -name "*.map"

# Analyze original source structure
npx source-map-explorer bundle.js bundle.js.map
```

## Expected React Native Artifacts

### API Service Files

- Centralized API service classes
- HTTP client configurations
- Environment-specific endpoints
- Authentication service URLs

### State Management

- Redux actions with API calls
- Saga/Thunk effects
- Context API with network calls
- Apollo/Relay GraphQL configs

### Navigation & Deep Links

- URL schemes and deep links
- WebView external URLs
- Share and social media URLs

## Output Format

```bash
# [ENDPOINT_NAME] - Found in [BUNDLE_LOCATION] 
curl -X [METHOD] "[FULL_URL]" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer [TOKEN]"

# Example from React Native bundle
# User API - Found in index.android.bundle line 1247
curl -X GET "https://api.reactapp.com/v1/users" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer [JWT_TOKEN]"

# Login endpoint - Found in authentication service
curl -X POST "https://api.reactapp.com/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'
```

## React Native Specific Challenges

1. **Minified Code**: JavaScript is heavily minified/uglified
2. **Bundle Splitting**: Code might be split across multiple bundles
3. **Hermes Bytecode**: Some apps use Hermes for better performance
4. **Metro Bundler**: Special bundling with React Native transforms
5. **Native Modules**: Some URLs might be in native Android/iOS code

## Analysis Priority

1. **Extract Bundle**: Get the main JavaScript bundle
2. **Beautify Code**: Make minified code readable
3. **Search Patterns**: Look for common API patterns
4. **Deobfuscate**: Handle encoded/obfuscated URLs
5. **Native Check**: Verify no URLs in native modules

## Common Gotchas

- URLs might be dynamically constructed at runtime
- Environment variables replaced at build time
- Some endpoints only in development bundles
- GraphQL endpoints might use different patterns
- WebSocket URLs for real-time features

Focus on extracting the JavaScript bundle first, then systematically search for
all HTTP/HTTPS patterns while handling the various obfuscation techniques
commonly used in React Native apps.
