FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="${PATH}:/tools/apktool:/tools/dex2jar:/tools/jadx/bin"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    openjdk-17-jdk \
    python3 \
    python3-pip \
    wget \
    unzip \
    git \
    curl \
    bash \
    nodejs \
    npm \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Claude Code CLI
RUN curl -fsSL https://claude.ai/install.sh | bash

# Create tools directory
RUN mkdir -p /tools /data

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

# Install reflutter
RUN pip3 install reflutter

# Create symbolic links for easier access
RUN ln -s /tools/dex2jar/d2j-dex2jar.sh /usr/local/bin/d2j-dex2jar && \
    ln -s /tools/dex2jar/d2j-jar2dex.sh /usr/local/bin/d2j-jar2dex && \
    ln -s /tools/apktool/apktool /usr/local/bin/apktool && \
    ln -s /tools/jadx/bin/jadx /usr/local/bin/jadx && \
    ln -s /tools/jadx/bin/jadx-gui /usr/local/bin/jadx-gui

# Set working directory
WORKDIR /data

# Entrypoint will be mounted from host via docker-compose
# Default entrypoint for direct docker run (fallback)
ENTRYPOINT ["/docker/entrypoint.sh"]
