# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Nggasak is an authorized application analysis tool designed for comprehensive security testing and reverse engineering of applications with proper permissions. The name "Nggasak" comes from Javanese meaning "to extract/dismantle completely" - reflecting the tool's thorough analysis capabilities.

## Core Philosophy

Based on FILOSOFI.md, this tool emphasizes:
- **Totalitas**: Complete analysis from surface to deep structure
- **Strategic Analysis**: Methodical sniffing, tracing, and reverse engineering
- **Truth over Appearance**: Focus on uncovering hidden functionality rather than UI analysis
- **Authorized Security Research**: Extracting APIs, payloads, encryption signatures, and communication patterns


## Plan & Review

### Before starting work

- Always in plan mode to make a plan
- After get the plan, make sure you Write the plan to .claude/tasks/TASK_NAME.md.
- The plan should be a detailed implementation plan and the reasoning behind them, as well as tasks broken down.
- If the task require external knowledge or certain package, also research to get latest knowledge (Use Task tool for research)
- Don't over plan it, always think MVP.
- Once you write the plan, firstly ask me to review it. Do not continue until I approve the plan.

### While implementing

- You should update the plan as you work.
- After you complete tasks in the plan, you should update and append detailed descriptions of the changes you made, so following tasks can be easily hand over to other engineers.


## Project Structure

This is currently an early-stage project with minimal codebase. The repository contains:
- `FILOSOFI.md`: Core project philosophy and naming rationale
- `README.md`: Basic project documentation
- `CLAUDE.md`: This guidance file

## Docker Usage

The project is intended to use Docker for containerized analysis environments, though Docker configuration files are not yet present in the codebase.

## Development Guidelines

### Security and Ethics
- This tool is designed for authorized analysis only
- Always ensure proper permissions before analyzing any application
- Focus on defensive security research and vulnerability assessment
- Document analysis scope and authorization clearly

### Architecture Considerations
- Design for containerized deployment using Docker
- Plan for modular analysis components (API discovery, encryption analysis, communication tracing)

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
  # Launch Claude Code for interactive analysis (always use --dangerously-skip-permissions for RE work)
  claude --dangerously-skip-permissions
  
  # Analyze decompiled APK structure
  claude --dangerously-skip-permissions "analyze this decompiled APK structure and identify key components"
  
  # Generate analysis scripts
  claude --dangerously-skip-permissions "create a script to extract API endpoints from this smali code"
  
  # Code pattern detection
  claude --dangerously-skip-permissions "find encryption/obfuscation patterns in these Java files"
  ```

### Core APK Analysis Tools
- **apktool** - Decompile APK to smali code and resources
  ```bash
  apktool d app.apk
  apktool b decompiled_app/
  ```
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