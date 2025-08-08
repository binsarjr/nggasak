# Nggasak

Reverse-engineering workspace for authorized APK analysis: decompile, trace, and extract real API endpoints fast.

## What’s inside
- Dockerized toolchain: apktool, dex2jar, jadx, reflutter, Claude Code CLI
- Script: `scripts/extract_endpoints.py` to collect URLs/endpoints into `analysis/curl.txt`
- Folders: `data/` (inputs), `analysis/` (outputs)

## Quick start
1) Prepare env
- Copy .env.example to .env and set ANTHROPIC_API_KEY if you’ll use Claude CLI.

2) Build and run container

```bash
# Build image
docker-compose build

# Start an interactive session
docker-compose run --rm nggasak-analyzer
```

3) Inside container, analyze an APK

```bash
# Decompile to smali/resources
apktool d app.apk -o /data/decompiled/

# Decompile Java sources
jadx app.apk -d /data/jadx_output/
```

4) On host, extract endpoints into curl templates

```bash
python3 scripts/extract_endpoints.py --root ./data/decompiled --out ./analysis/curl.txt
# or, for Java sources
python3 scripts/extract_endpoints.py --root ./data/jadx_output --out ./analysis/curl.txt
```

Open `analysis/curl.txt`, review, dedupe, add auth/payloads, and test.

## Make targets (optional)
```bash
make build    # docker-compose build
make up       # docker-compose up -d nggasak-analyzer
make exec     # docker-compose exec nggasak-analyzer bash
make extract  # run endpoint extractor from ./data/decompiled
```

## Ethics & scope
Use only on apps you’re authorized to test. See `FILOSOFI.md` for intent and philosophy.
