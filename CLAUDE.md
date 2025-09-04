# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with
code in this repository.

## Project Overview

Nggasak is an all-in-one Docker container for reverse engineering and security
analysis. The name "Nggasak" comes from Javanese meaning "to extract/dismantle
completely" - providing comprehensive analysis tools in a single container.

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

All-in-one container approach:

1. **Start Container**: `docker-compose up -d`
2. **Access Container**: `docker exec -it nggasak-analysis bash`
3. **Full Project Access**: Entire project mounted at `/workspace`
4. **Use Any Tool**: All RE tools pre-installed and ready
5. **Use Claude from Host**: Access Claude CLI from host system

## All-in-One RE Tools

### 📱 Mobile Application Analysis
- **apktool** - APK decompile/recompile: `apktool d app.apk`
- **jadx** - Java decompiler: `jadx app.apk -d output/`
- **dex2jar** - DEX to JAR: `d2j-dex2jar app.apk`
- **reflutter** - Flutter analysis: `reflutter app.apk`
- **androguard** - Python Android analysis library

### 🔍 Binary Analysis & Reverse Engineering
- **radare2** - Advanced binary analysis: `r2 binary`
- **binwalk** - Firmware analysis: `binwalk firmware.bin`
- **strings** - Extract strings: `strings binary`
- **objdump** - Object file analysis: `objdump -d binary`
- **hexdump** - Hex viewer: `hexdump -C file`

### 🔐 Cryptography & Password Tools
- **openssl** - Crypto operations: `openssl enc -aes-256-cbc`
- **hashcat** - Password cracking: `hashcat -m 0 hash.txt wordlist.txt`
- **john** - Password cracking: `john --wordlist=rockyou.txt hashes.txt`

### 🌐 Network Analysis
- **nmap** - Network scanner: `nmap -sV target`
- **netcat** - Network utility: `nc -lvp 4444`
- **tcpdump** - Packet capture: `tcpdump -i eth0`
- **tshark** - Wireshark CLI: `tshark -i eth0`

### 🐍 Python Security Libraries
- **frida** - Dynamic instrumentation
- **objection** - Mobile security testing
- **capstone** - Disassembly engine
- **yara** - Pattern matching
- **scapy** - Packet manipulation

### Analysis Workflow Examples

```bash
# Mobile app analysis
apktool d app.apk -o decompiled/
jadx app.apk -d jadx_output/
strings app.apk | grep -i api

# Binary reverse engineering
radare2 -A binary
binwalk -e firmware.bin
strings binary | grep -E "(password|key|token)"

# Network analysis
nmap -sS -O target_ip
tcpdump -i any port 443

# Crypto analysis
openssl x509 -in cert.pem -text
hashcat -m 1400 sha256_hashes.txt rockyou.txt

# Extract endpoints from APK
strings app.apk | grep -E "(http|https|api)" | sort -u
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
