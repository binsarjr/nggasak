FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV ANDROID_HOME=/tools/android-sdk
ENV PATH="${PATH}:/tools/apktool:/tools/dex2jar:/tools/jadx/bin:${ANDROID_HOME}/cmdline-tools/latest/bin:${ANDROID_HOME}/platform-tools"

# Install system dependencies
RUN apt-get update && apt-get install -y \
  openjdk-17-jdk \
  python3 \
  python3-pip \
  python3-dev \
  python3-venv \
  wget \
  unzip \
  git \
  curl \
  bash \
  nodejs \
  npm \
  ca-certificates \
  binutils \
  file \
  bsdmainutils \
  xxd \
  zip \
  p7zip-full \
  aapt \
  zipalign \
  build-essential \
  libssl-dev \
  libffi-dev \
  nmap \
  netcat-openbsd \
  tcpdump \
  tshark \
  openssl \
  jq \
  binwalk \
  john \
  hashcat \
  cmake \
  && rm -rf /var/lib/apt/lists/*

# Install Radare2 from source (lightweight installation)
RUN git clone --depth 1 https://github.com/radareorg/radare2 /tmp/radare2 && \
    cd /tmp/radare2 && \
    ./sys/install.sh && \
    cd / && \
    rm -rf /tmp/radare2

# Note: strings command is part of binutils package (already installed)
# Create tools directory
RUN mkdir -p /tools

# Install apktool
WORKDIR /tools/apktool
RUN wget https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool -O apktool && \
  chmod +x apktool && \
  wget https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_2.9.3.jar -O apktool.jar

# Install dex2jar
WORKDIR /tools
RUN wget https://github.com/pxb1988/dex2jar/releases/download/v2.4/dex-tools-v2.4.zip && \
  unzip dex-tools-v2.4.zip && \
  mv dex-tools-v2.4 dex2jar && \
  chmod +x dex2jar/*.sh && \
  rm dex-tools-v2.4.zip

# Install jadx
WORKDIR /tools
RUN wget https://github.com/skylot/jadx/releases/download/v1.4.7/jadx-1.4.7.zip && \
  unzip jadx-1.4.7.zip -d jadx && \
  chmod +x jadx/bin/jadx* && \
  rm jadx-1.4.7.zip

# Install baksmali/smali (standalone)
# WORKDIR /tools
# RUN wget https://github.com/JesusFreke/smali/archive/refs/tags/v2.5.2.zip -O smali.zip && \
#   unzip smali.zip && \
#   cd smali-2.5.2 && \
#   ./gradlew build && \
#   cp baksmali/build/libs/baksmali-2.5.2.jar /tools/baksmali.jar && \
#   cp smali/build/libs/smali-2.5.2.jar /tools/smali.jar && \
#   cd .. && \
#   rm -rf smali-2.5.2 smali.zip && \
#   echo '#!/bin/bash\njava -jar /tools/baksmali.jar "$@"' > /usr/local/bin/baksmali && \
#   echo '#!/bin/bash\njava -jar /tools/smali.jar "$@"' > /usr/local/bin/smali && \
#   chmod +x /usr/local/bin/baksmali /usr/local/bin/smali

# Install Python tooling (skip keystone-engine due to build issues)
RUN pip3 install --no-cache-dir \
  reflutter \
  frida-tools \
  objection \
  requests \
  beautifulsoup4 \
  lxml \
  pycryptodome \
  androguard \
  capstone \
  unicorn \
  yara-python \
  pyelftools \
  pefile \
  cryptography \
  scapy

# Create symbolic links for easier access
RUN ln -s /tools/dex2jar/d2j-dex2jar.sh /usr/local/bin/d2j-dex2jar && \
  ln -s /tools/dex2jar/d2j-jar2dex.sh /usr/local/bin/d2j-jar2dex && \
  ln -s /tools/apktool/apktool /usr/local/bin/apktool && \
  ln -s /tools/jadx/bin/jadx /usr/local/bin/jadx && \
  ln -s /tools/jadx/bin/jadx-gui /usr/local/bin/jadx-gui

# Install Android SDK command line tools (for apksigner, keytool)
WORKDIR /tools
RUN wget https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip && \
  unzip commandlinetools-linux-11076708_latest.zip && \
  rm commandlinetools-linux-11076708_latest.zip && \
  mkdir -p android-sdk/cmdline-tools && \
  mv cmdline-tools android-sdk/cmdline-tools/latest && \
  export ANDROID_HOME=/tools/android-sdk && \
  export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin && \
  ln -s /tools/android-sdk/cmdline-tools/latest/bin/apksigner /usr/local/bin/apksigner || true

# Copy entrypoint as a fallback if volume not mounted
COPY docker/entrypoint.sh /docker/entrypoint.sh
RUN chmod +x /docker/entrypoint.sh

# Create non-root user
RUN useradd -ms /bin/bash nggasak

# Switch to non-root user
USER nggasak
WORKDIR /workspace

# Entrypoint (can be overridden by docker-compose volume mount)
ENTRYPOINT ["/docker/entrypoint.sh"]
