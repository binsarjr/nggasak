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
    && rm -rf /var/lib/apt/lists/*

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

# Create entrypoint script for easy access to tools
RUN echo '#!/bin/bash\n# Auto-detect JAVA_HOME\nexport JAVA_HOME=$(dirname $(dirname $(readlink -f $(which java))))\necho "Nggasak Analysis Tools Container"\necho "Available tools:"\necho "- apktool ($(apktool --version 2>&1 | head -1))"\necho "- dex2jar (d2j-dex2jar)"\necho "- jadx ($(jadx --version 2>&1 | head -1))"\necho "- reflutter ($(reflutter --version 2>&1 | head -1))"\necho ""\necho "Working directory: /data"\necho "All tools are in PATH. Example usage:"\necho "  apktool d app.apk"\necho "  d2j-dex2jar app.apk"\necho "  jadx app.apk -d output/"\necho "  reflutter app.apk"\necho ""\nif [ "$#" -eq 0 ]; then\n  exec /bin/bash\nelse\n  exec "$@"\nfi' > /usr/local/bin/entrypoint.sh && \
    chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
