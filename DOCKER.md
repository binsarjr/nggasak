# Nggasak Docker Setup

Docker environment untuk reverse engineering tools APK analysis.

## Quick Start

### Build dan Run Container
```bash
# Build image
docker-compose build

# Run interactive container
docker-compose up -d nggasak-analyzer
docker-compose exec nggasak-analyzer bash

# Atau langsung run
docker-compose run --rm nggasak-analyzer
```

### Tool Usage

#### 1. APKTool - Decompile APK
```bash
# Decompile APK
apktool d app.apk -o decompiled_app/

# Recompile
apktool b decompiled_app/ -o recompiled.apk
```

#### 2. dex2jar - Convert DEX to JAR
```bash
# Convert APK to JAR
d2j-dex2jar app.apk -o app.jar

# Convert DEX to JAR
d2j-dex2jar classes.dex -o classes.jar
```

#### 3. JADX - Java Decompiler
```bash
# Decompile APK to Java source
jadx app.apk -d jadx_output/

# With specific options
jadx app.apk -d output/ --show-bad-code --escape-unicode
```

#### 4. ReFlutter - Flutter App Analysis
```bash
# Analyze Flutter app
reflutter app.apk

# Extract and patch
reflutter app.apk --extract
```

## Folder Structure

- `./data/` - Input APK files dan working directory
- `./analysis/` - Output hasil analisis
- Container working dir: `/data`

## Advanced Usage

### Web Interface (Optional)
```bash
# Run jadx with web interface
docker-compose --profile web up jadx-web

# Access via browser: http://localhost:8080
```

### Custom Commands
```bash
# Run specific command
docker-compose run --rm nggasak-analyzer apktool d myapp.apk

# Mount additional volumes
docker-compose run --rm -v $(pwd)/extra:/extra nggasak-analyzer bash
```

## Tool Versions

- **apktool**: 2.9.3
- **dex2jar**: 2.4  
- **jadx**: 1.4.7
- **reflutter**: Latest from pip

## Workflow Example

```bash
# 1. Place APK in data/ folder
cp myapp.apk ./data/

# 2. Start container
docker-compose run --rm nggasak-analyzer

# 3. Inside container - analyze APK
apktool d myapp.apk -o decompiled/
jadx myapp.apk -d jadx_out/
d2j-dex2jar myapp.apk -o myapp.jar
reflutter myapp.apk

# 4. Results available in data/ and analysis/ folders
```

## Troubleshooting

### Permission Issues
```bash
# Fix permissions if needed
sudo chown -R $USER:$USER ./data ./analysis
```

### Container Rebuild
```bash
# Rebuild if tools need update
docker-compose build --no-cache nggasak-analyzer
```
