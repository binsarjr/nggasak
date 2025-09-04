# Nggasak - All-in-One Reverse Engineering Container

> **Nggasak** (Javanese: "to extract/dismantle completely") - A comprehensive Docker container for reverse engineering and security analysis.

## 🎯 Overview

Nggasak provides a complete, pre-configured environment for reverse engineering mobile applications, binaries, and conducting security analysis. Everything runs in a single Docker container with all tools pre-installed and ready to use.

## ✨ Features

- **All-in-One Container**: Single Docker container with 40+ security tools
- **Mobile RE Focus**: Specialized tools for Android APK analysis
- **Binary Analysis**: Complete toolkit for binary reverse engineering
- **Network Security**: Built-in network analysis and scanning tools
- **Zero Configuration**: Works immediately after container start
- **Project Mounting**: Full access to your project files from container

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/binsarjr/nggasak.git
   cd nggasak
   ```

2. **Start the container**
   ```bash
   docker-compose up -d
   ```

3. **Access the container**
   ```bash
   docker exec -it nggasak-analysis bash
   ```

## 🛠️ Available Tools

### Mobile Application Analysis
| Tool | Purpose | Example Usage |
|------|---------|---------------|
| **apktool** | Decompile/recompile APK | `apktool d app.apk` |
| **jadx** | Java decompiler | `jadx app.apk -d output/` |
| **dex2jar** | Convert DEX to JAR | `d2j-dex2jar app.apk` |
| **reflutter** | Flutter app analysis | `reflutter app.apk` |
| **androguard** | Android analysis library | Python import |

### Binary Analysis & RE
| Tool | Purpose | Example Usage |
|------|---------|---------------|
| **radare2** | Binary analysis framework | `r2 -A binary` |
| **binwalk** | Firmware extraction | `binwalk -e firmware.bin` |
| **strings** | Extract text strings | `strings binary \| grep api` |
| **objdump** | Object file analysis | `objdump -d binary` |

### Network Analysis
| Tool | Purpose | Example Usage |
|------|---------|---------------|
| **nmap** | Network scanner | `nmap -sV target` |
| **tcpdump** | Packet capture | `tcpdump -i any port 443` |
| **tshark** | Protocol analyzer | `tshark -i eth0` |
| **netcat** | Network utility | `nc -lvp 4444` |

### Cryptography & Passwords
| Tool | Purpose | Example Usage |
|------|---------|---------------|
| **hashcat** | Password cracking | `hashcat -m 0 hash.txt wordlist.txt` |
| **john** | Password cracking | `john --wordlist=rockyou.txt hashes.txt` |
| **openssl** | Crypto operations | `openssl enc -aes-256-cbc` |

## 📚 Common Workflows

### Android APK Analysis
```bash
# 1. Decompile APK
apktool d target.apk -o decompiled/

# 2. Convert to Java source
jadx target.apk -d jadx_output/

# 3. Extract strings and endpoints
strings target.apk | grep -E "(http|https|api)" | sort -u

# 4. Search for sensitive data
grep -r "password\|key\|token\|secret" decompiled/
```

### Binary Reverse Engineering
```bash
# 1. Initial analysis
file target_binary
strings target_binary | head -50

# 2. Deep analysis with radare2
r2 -A target_binary
[0x00000000]> afl  # List functions
[0x00000000]> pdf @ main  # Disassemble main

# 3. Extract embedded files
binwalk -e target_binary
```

### Network Analysis
```bash
# 1. Scan target
nmap -sS -sV -O target_ip

# 2. Capture traffic
tcpdump -i any -w capture.pcap host target_ip

# 3. Analyze with tshark
tshark -r capture.pcap -Y "http.request"
```

## 📁 Project Structure

```
nggasak/
├── docker/
│   └── entrypoint.sh      # Container initialization script
├── workspace/              # Your analysis files (mounted volume)
├── Dockerfile              # Container definition
├── docker-compose.yml      # Service configuration
├── CLAUDE.md              # AI assistant instructions (for host Claude)
├── FILOSOFI.md            # Project philosophy
└── README.md              # This file
```

## 🔧 Configuration

### Docker Compose

The `docker-compose.yml` mounts your current directory to `/workspace` in the container, giving you full access to your files. No additional configuration is required - all tools are pre-installed and ready to use.

## 💡 Tips & Best Practices

1. **Always work in `/workspace`** - This is where your project files are mounted
2. **Use Claude from host system** - Run Claude Code on your host machine to analyze results from the container
3. **Save analysis results** - Output important findings to files in `/workspace` for Claude to analyze
4. **Chain tools together** - Combine multiple tools for comprehensive analysis
5. **Check permissions** - Ensure you have authorization before analyzing any application

## 🔒 Security & Ethics

⚠️ **IMPORTANT**: This tool is for authorized security research only.

- Only analyze applications you own or have explicit permission to test
- Follow responsible disclosure practices
- Document your authorization and scope
- Use for defensive security and vulnerability assessment
- Never use for malicious purposes

## 🐛 Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs -f

# Rebuild if needed
docker-compose build --no-cache
```

### Permission denied errors
```bash
# Run as root user if needed
docker exec -it --user root nggasak-analysis bash
```

### Tool not found
```bash
# Check PATH
echo $PATH

# Tools are installed in:
# /tools/apktool, /tools/jadx/bin, /tools/dex2jar
# /usr/local/bin, /usr/bin
```

## 📖 Documentation

- [CLAUDE.md](./CLAUDE.md) - Instructions for Claude Code when analyzing results (used on host)
- [FILOSOFI.md](./FILOSOFI.md) - Project philosophy and principles
- [Docker Documentation](https://docs.docker.com/)

## 🤝 Contributing

Contributions are welcome! Please ensure:
1. Tools added are relevant to reverse engineering/security analysis
2. Documentation is updated
3. Container size is kept reasonable
4. Security best practices are followed

## 📄 License

This project is for educational and authorized security research purposes only. Users are responsible for complying with all applicable laws and regulations.

## 🙏 Acknowledgments

Built with tools from:
- [iBotPeaches/Apktool](https://github.com/iBotPeaches/Apktool)
- [skylot/jadx](https://github.com/skylot/jadx)
- [radareorg/radare2](https://github.com/radareorg/radare2)
- [frida/frida](https://github.com/frida/frida)
- And many other open-source security tools

---

**Remember**: With great power comes great responsibility. Use these tools ethically and legally.