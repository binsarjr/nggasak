# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with
code in this repository.

## Project Overview

Nggasak is a simple Docker container for reverse engineering and security
analysis of mobile applications. The name "Nggasak" comes from Javanese meaning
"to extract/dismantle completely" - reflecting comprehensive analysis
capabilities.

## Core Philosophy

Based on FILOSOFI.md, this tool emphasizes:

- **Totalitas**: Complete analysis from surface to deep structure
- **Strategic Analysis**: Methodical reverse engineering with proper tools
- **Truth over Appearance**: Focus on uncovering hidden functionality
- **Authorized Security Research**: For applications you have permission to
  analyze

## Plan & Review

### Before starting work

- Always in plan mode to make a plan
- After get the plan, make sure you Write the plan to
  .claude/tasks/TASK_NAME.md.
- The plan should be a detailed implementation plan and the reasoning behind
  them, as well as tasks broken down.
- If the task require external knowledge or certain package, also research to
  get latest knowledge (Use Task tool for research)
- Don't over plan it, always think MVP.
- Once you write the plan, firstly ask me to review it. Do not continue until I
  approve the plan.

### While implementing

- You should update the plan as you work.
- After you complete tasks in the plan, you should update and append detailed
  descriptions of the changes you made, so following tasks can be easily hand
  over to other engineers.

## Simple Docker Workflow

This is a simple Docker container approach:

1. **Start Container**: `docker-compose up -d`
2. **Access Container**: `docker exec -it nggasak-analysis bash`
3. **Place APKs**: Put APK files in `./data/` folder (mounted as `/data`)
4. **Use Tools Manually**: Run analysis tools as needed
5. **Use Claude**: Run `claude` for AI-powered analysis inside container

## Reverse Engineering Tools

All tools are pre-installed and available via command line:

### Core APK Analysis Tools

- **apktool** - Decompile APK to smali code and resources
  ```bash
  apktool d app.apk -o decompiled/
  apktool b decompiled_app/
  ```
- **dex2jar** - Convert DEX files to JAR format
  ```bash
  d2j-dex2jar app.apk -o target.jar
  ```
- **jadx** - Java decompiler for Android apps
  ```bash
  jadx app.apk -d jadx_output/
  ```
- **reflutter** - Flutter app analysis and patching
  ```bash
  reflutter app.apk
  ```

### Claude Code Integration

- **claude** - AI-powered analysis inside the container
  ```bash
  # Analyze decompiled code
  claude "analyze this decompiled APK structure"
  
  # Find patterns
  claude "find encryption patterns in Java code"
  
  # Extract APIs
  claude "extract API endpoints from this code"
  ```

### Analysis Workflow Examples

```bash
# Basic workflow
apktool d target.apk -o decompiled/
jadx target.apk -d jadx_output/
claude "analyze the decompiled APK in /data/decompiled/"

# Flutter analysis
reflutter target.apk
claude "analyze the extracted Flutter code"

# Deep analysis
d2j-dex2jar target.apk -o target.jar
claude "find security vulnerabilities in the Java code"
```

## Environment Setup

Required environment variable in `.env` file:
```bash
ANTHROPIC_API_KEY="your_claude_api_key_here"
```

Optional variables:
- `ANTHROPIC_BASE_URL` - Alternative API endpoint
- `ANTHROPIC_AUTH_TOKEN` - Alternative to API key

## Docker Commands

```bash
# Build and start
docker-compose up -d

# Access shell
docker exec -it nggasak-analysis bash

# View logs  
docker-compose logs -f

# Stop
docker-compose down
```

## Security and Ethics

- This tool is designed for authorized analysis only
- Always ensure proper permissions before analyzing any application
- Focus on defensive security research and vulnerability assessment
- Document analysis scope and authorization clearly

## Technology Stack

- **Docker** - Containerized analysis environment
- **Ubuntu 22.04** - Base system with Java 17
- **Claude Code CLI** - AI-powered analysis
- **Static analysis tools** - apktool, jadx, dex2jar, reflutter
