#!/bin/bash

# Auto-detect JAVA_HOME
export JAVA_HOME=$(dirname $(dirname $(readlink -f $(which java))))

echo "🔍 Nggasak All-in-One RE Tools Container"
echo ""
echo "📱 Mobile Analysis: apktool, jadx, dex2jar, reflutter, androguard"
echo "🔍 Binary Analysis: radare2, binwalk, strings, hexdump, objdump"
echo "🔐 Crypto Tools: openssl, hashcat, john"
echo "🌐 Network Tools: nmap, netcat, tcpdump, tshark"
echo "🐍 Python Libraries: frida, objection, capstone, yara, scapy"
echo "📁 Project mounted at: /workspace"
echo ""

# Execute the command or start bash
if [ "$#" -eq 0 ]; then
    exec /bin/bash
else
    exec "$@"
fi
