# Docker Setup for Nggasak Analysis Tools

## Goal
Menyediakan environment containerized untuk menjalankan tool reverse engineering APK: apktool, dex2jar, jadx, dan reflutter.

## Rencana Implementasi

### 1. Dockerfile
- Base image: Ubuntu (latest stable)
- Install dependencies: openjdk, python3, wget, unzip, git
- Install apktool (download jar + wrapper script)
- Install dex2jar (download release zip)
- Install jadx (download release zip)
- Install reflutter (install via pip)
- Set PATH agar semua tool bisa diakses dari shell

### 2. docker-compose.yml
- Satu service utama: "nggasak-analyzer"
- Mount volume ke folder kerja lokal agar hasil analisis bisa diakses
- Expose folder /data untuk input/output APK

### 3. Struktur Folder
- /tools: tempat installasi tool
- /data: tempat input/output APK dan hasil analisis

### 4. Testing
- Jalankan container, cek versi masing-masing tool

## Task Breakdown
1. ✅ Buat Dockerfile sesuai spesifikasi di atas - SELESAI
2. ✅ Buat docker-compose.yml untuk service utama - SELESAI
3. ✅ Dokumentasi cara build dan run - SELESAI (DOCKER.md)
4. ✅ Validasi instalasi tool dengan perintah versi - SELESAI

## IMPLEMENTASI COMPLETED

### Yang sudah dibuat:
1. **Dockerfile** - Base Ubuntu 22.04 dengan semua tools:
   - apktool 2.9.3 
   - dex2jar v2.4
   - jadx 1.4.7
   - reflutter (latest via pip)
   - Auto-detect JAVA_HOME untuk compatibility

2. **docker-compose.yml** - Service nggasak-analyzer dengan:
   - Volume mount /data dan /analysis
   - Interactive terminal access
   - Optional web service untuk jadx-gui

3. **Folder struktur**:
   - `/data` - Input APK files
   - `/analysis` - Output hasil analisis

4. **Dokumentasi lengkap** di DOCKER.md dengan:
   - Quick start guide
   - Usage examples untuk setiap tool
   - Workflow example
   - Troubleshooting

### Testing Results:
- ✅ apktool: version 2.9.3 working
- ✅ dex2jar: version 2.4 working  
- ✅ jadx: version 1.4.7 working
- ✅ reflutter: working (no --version flag available)

### Usage:
```bash
# Build
docker-compose build

# Run interactive
docker-compose run --rm nggasak-analyzer

# Test tools
docker-compose run --rm nggasak-analyzer bash -c "apktool --version"
```
