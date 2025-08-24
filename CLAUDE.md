# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with
code in this repository.

## Project Overview

Nggasak is an authorized application analysis tool designed for comprehensive
security testing and reverse engineering of applications with proper
permissions. The name "Nggasak" comes from Javanese meaning "to
extract/dismantle completely" - reflecting the tool's thorough analysis
capabilities.

## Core Philosophy

Based on FILOSOFI.md, this tool emphasizes:

- **Totalitas**: Complete analysis from surface to deep structure
- **Strategic Analysis**: Methodical sniffing, tracing, and reverse engineering
- **Truth over Appearance**: Focus on uncovering hidden functionality rather
  than UI analysis
- **Authorized Security Research**: Extracting APIs, payloads, encryption
  signatures, and communication patterns

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

## Project Structure

This is currently an early-stage project with minimal codebase. The repository
contains:

- `FILOSOFI.md`: Core project philosophy and naming rationale
- `README.md`: Basic project documentation
- `CLAUDE.md`: This guidance file

## Docker Usage

The project is intended to use Docker for containerized analysis environments,
though Docker configuration files are not yet present in the codebase.

## Development Guidelines

### Security and Ethics

- This tool is designed for authorized analysis only
- Always ensure proper permissions before analyzing any application
- Focus on defensive security research and vulnerability assessment
- Document analysis scope and authorization clearly

### Architecture Considerations

- Design for containerized deployment using Docker
- Plan for modular analysis components (API discovery, encryption analysis,
  communication tracing)

## Future Development Areas

Based on the project philosophy, key areas to implement:

- API endpoint discovery and mapping
- Payload structure analysis
- Encryption signature detection
- App-server communication pattern analysis
- Reverse engineering toolchain integration

## Reverse Engineering Tools

### Primary Analysis Tool

- **Claude Code** - AI-powered reverse engineering assistant
  ```bash
  # Launch Claude Code for interactive analysis
  claude

  # Analyze decompiled APK structure
  claude "analyze this decompiled APK structure and identify key components"

  # Generate analysis scripts
  claude "create a script to extract API endpoints from this smali code"

  # Code pattern detection
  claude "find encryption/obfuscation patterns in these Java files"
  ```

Note: The flag --dangerously-skip-permissions is not allowed when running as
root/sudo inside the container and will fail. Use plain `claude` without the
flag.

````
### Core APK Analysis Tools
- **apktool** - Decompile APK to smali code and resources
```bash
apktool d app.apk
apktool b decompiled_app/
````

- **dex2jar** - Convert DEX files to JAR format
  ```bash
  d2j-dex2jar app.apk
  ```
- **jadx** - Java decompiler for Android apps
  ```bash
  jadx app.apk
  ```

### Framework-Specific Tools

- **ReFlutter** - Flutter app analysis and patching
  ```bash
  reflutter app.apk
  ```

### Analysis Commands

Common workflow for APK analysis:

```bash
# Basic decompilation
apktool d target.apk -o decompiled/
jadx target.apk -d jadx_output/

# DEX to JAR conversion
d2j-dex2jar target.apk -o target.jar

# Flutter-specific analysis
reflutter target.apk
```

## Claude Code Limitations

### CLI-Only Capabilities

Claude Code can only work with:

- Code-based analysis and file manipulation
- CLI tools and command execution
- Static analysis of decompiled code
- Script automation and tool integration

### Cannot Handle

- Device or emulator operations
- Runtime dynamic analysis requiring physical/virtual devices
- GUI-based tools interaction
- Real-time debugging on running applications
- Network traffic interception requiring device setup

## Technology Stack

Recommended stack for CLI-based analysis:

- **Python** - Analysis scripts and automation
- **Docker** - Containerized analysis environments
- **Shell scripts** - Tool integration and workflow automation
- **Static analysis tools** - apktool, jadx, dex2jar, reflutter

## Automated Ingestion and Analysis Queue

Nggasak runs as an automated system: whenever an `.apk` or `.xapk` file is
placed in the `data/` folder, it is automatically queued for analysis. Each
artifact is processed one-by-one to ensure reproducibility and clear outputs.

High-level flow per file (MVP):

- Detect new `.apk`/`.xapk` inside `data/`
- For `.xapk`, extract and select the primary/base APK
- Decompile with `apktool` and `jadx`
- Perform code analysis with Claude Code CLI (if API key is configured)
- Save all results under `analysis/<app_basename>/`

Outputs per artifact (example):

- `analysis/<name>/decompiled/` – apktool output
- `analysis/<name>/jadx_output/` – JADX decompiled sources
- `analysis/<name>/curl.txt` – auto-generated cURL templates of discovered
  endpoints
- `analysis/<name>/ai_analysis.txt` – Claude Code summary (if enabled)
- `analysis/.processed/<original_filename>.done` – marker for processed inputs

How to run the queue in Docker:

- One-shot process everything pending: `make process-once`
- Continuous watch mode: `make watch`

Environment variables:

- `ANTHROPIC_API_KEY` – Claude API key used by the CLI
- `ANTHROPIC_AUTH_TOKEN` – alternative var name; if set, it will be mapped to
  `ANTHROPIC_API_KEY`
- `ANTHROPIC_BASE_URL` – optional alternative base URL for the Claude CLI
- `AUTO_WATCH=1` – if set for the container entrypoint (future), start watcher
  automatically

Notes:

- Only authorized analysis is allowed. Ensure you have permission to analyze
  each application.
- If Claude CLI isn't configured, the pipeline still produces decompilations and
  endpoint extraction.
