#!/usr/bin/env python3
"""
Auto-queue watcher for APK/XAPK files in ./data.

NEW STEP-BASED APPROACH:
- Scans ./data for *.apk and *.xapk files.
- Processes each file once, writing a marker into ./analysis/.processed/<filename>.done
- Enhanced 3-step analysis per artifact:
  1) For XAPK: unzip and pick base APK (the largest or file containing 'base' in name)
  2) Decompile via apktool -> analysis/<name>/decompiled
  3) Decompile via jadx -> analysis/<name>/jadx_output
  4) STEP 1: Identify app type (Native Android, Flutter, React Native, etc.)
  5) STEP 2: Select appropriate tools based on app type
  6) STEP 3: Run specialized analysis with targeted prompts
  7) Extract endpoints -> analysis/<name>/curl.txt (enhanced)
  8) Generate comprehensive analysis report

Requirements: apktool, jadx, claude CLI available in PATH (Docker image provides these).

Usage:
  - One-shot process: python3 scripts/auto_queue.py --once
  - Watch mode:      python3 scripts/auto_queue.py --watch
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ANALYSIS_DIR = ROOT / "analysis"
PROCESSED_DIR = ANALYSIS_DIR / ".processed"
SCRIPTS_DIR = ROOT / "scripts"


def log(msg: str) -> None:
    print(f"[auto-queue] {msg}", flush=True)


def run(cmd: list[str], cwd: Optional[Path] = None, env: Optional[dict] = None) -> int:
    log("$ " + " ".join(cmd))
    try:
        res = subprocess.run(cmd, cwd=str(cwd) if cwd else None, env=env, check=False)
        return res.returncode
    except FileNotFoundError:
        log(f"Command not found: {cmd[0]}")
        return 127


def find_base_apk(xapk_path: Path, temp_dir: Path) -> Optional[Path]:
    """Extract XAPK and return a likely base APK path."""
    extract_dir = temp_dir / xapk_path.stem
    extract_dir.mkdir(parents=True, exist_ok=True)
    rc = run(["unzip", "-o", str(xapk_path), "-d", str(extract_dir)])
    if rc != 0:
        log(f"Failed to unzip {xapk_path}")
        return None
    apks = list(extract_dir.rglob("*.apk"))
    if not apks:
        log("No APK found inside XAPK")
        return None
    # 1) exact base.apk
    for p in apks:
        if p.name.lower() == "base.apk":
            return p
    # 2) name contains 'base'
    base_candidates = [p for p in apks if "base" in p.name.lower()]
    if base_candidates:
        return max(base_candidates, key=lambda p: p.stat().st_size)
    # 3) avoid config.* splits if possible
    non_config = [p for p in apks if not p.name.lower().startswith("config")]
    if non_config:
        return max(non_config, key=lambda p: p.stat().st_size)
    # 4) fallback to largest
    return max(apks, key=lambda p: p.stat().st_size)


def decompile_with_apktool(apk: Path, out_dir: Path) -> bool:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    rc = run(["apktool", "d", str(apk), "-o", str(out_dir), "-f"])  # -f overwrite
    return rc == 0


def decompile_with_jadx(apk: Path, out_dir: Path) -> bool:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    rc = run(["jadx", str(apk), "-d", str(out_dir)])
    return rc == 0


def extract_endpoints(src_root: Path, out_file: Path) -> bool:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    rc = run(["python3", str(SCRIPTS_DIR / "extract_endpoints.py"), "--root", str(src_root), "--out", str(out_file)])
    return rc == 0


def step_based_analysis(work_dir: Path) -> bool:
    """
    Run the new 3-step analysis pipeline instead of the old simple AI analysis.
    
    Steps:
    1. Identify app type (Native Android, Flutter, React Native, etc.)
    2. Select appropriate tools based on app type  
    3. Run specialized analysis with targeted prompts
    """
    try:
        # Import the step runner
        import sys
        sys.path.append(str(SCRIPTS_DIR))
        from step_runner import run_step_based_analysis
        
        log("Starting step-based analysis pipeline...")
        
        # Run the complete pipeline
        results = run_step_based_analysis(work_dir)
        
        if "error" in results:
            log(f"Step-based analysis failed: {results['error']}")
            return False
        
        # Log summary of results
        summary = results.get('summary', {})
        log(f"Pipeline completed: {summary.get('app_type', 'Unknown')} app")
        log(f"Confidence: {summary.get('confidence', 'Unknown')}")
        log(f"Endpoints found: {summary.get('endpoints_found', 0)}")
        log(f"Curl commands generated: {summary.get('curl_commands_generated', 0)}")
        
        return True
        
    except ImportError as e:
        log(f"Failed to import step_runner: {e}")
        log("Falling back to legacy AI analysis...")
        return legacy_ai_analyze(work_dir)
    except Exception as e:
        log(f"Step-based analysis failed with error: {e}")
        log("Falling back to legacy AI analysis...")
        return legacy_ai_analyze(work_dir)


def legacy_ai_analyze(work_dir: Path) -> bool:
    """
    Legacy AI analysis function (backup if step-based fails).
    """
    src_root = work_dir / "jadx_output" if (work_dir / "jadx_output").exists() else work_dir / "decompiled"
    out_file = work_dir / "ai_analysis.txt"
    
    api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")
    if not api_key:
        log("Claude API key not configured; skipping AI analysis")
        return False
        
    env = dict(os.environ)
    env["ANTHROPIC_API_KEY"] = api_key
    base_url = os.environ.get("ANTHROPIC_BASE_URL")
    if base_url:
        env["ANTHROPIC_BASE_URL"] = base_url
        
    # Build lightweight context
    manifest = ""
    manifest_path = work_dir / "decompiled" / "AndroidManifest.xml"
    if manifest_path.exists():
        try:
            manifest = manifest_path.read_text(encoding="utf-8", errors="ignore")[:4000]
        except Exception:
            pass

    curl_snippet = ""
    curl_path = work_dir / "curl.txt"
    if curl_path.exists():
        try:
            curl_snippet = curl_path.read_text(encoding="utf-8", errors="ignore")[:4000]
        except Exception:
            pass

    file_list = []
    try:
        for i, p in enumerate(sorted(src_root.rglob("*"))):
            if p.is_file():
                file_list.append(str(p.relative_to(src_root)))
            if i > 400:
                break
    except Exception:
        pass

    context = (
        f"Decompiled root: {src_root}\n\n"
        "--- ANDROID MANIFEST (first 4000 chars) ---\n" + (manifest or "<not found>") + "\n\n"
        "--- DISCOVERED CURL ENDPOINTS (first 4000 chars) ---\n" + (curl_snippet or "<none>") + "\n\n"
        "--- FILE LIST (first ~400 files) ---\n" + "\n".join(file_list) + "\n"
    )

    prompt = (
        "You are analyzing a decompiled Android app. Using the snippets and file list below, summarize: "
        "(1) API usage/endpoints, (2) auth flows & tokens, (3) encryption/obfuscation, "
        "(4) sensitive data handling & permissions, (5) next steps for deeper RE. Keep it concise.\n\n"
        + context
    )
    cmd = ["claude", "--dangerously-skip-permissions", prompt]
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with out_file.open("w", encoding="utf-8") as f:
        try:
            res = subprocess.run(cmd, env=env, stdout=f, stderr=subprocess.STDOUT, check=False)
            return res.returncode == 0
        except FileNotFoundError:
            log("claude CLI not found; skipping AI analysis")
            return False


def marker_for(input_file: Path) -> Path:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    return PROCESSED_DIR / f"{input_file.name}.done"


def process_file(input_path: Path) -> bool:
    log(f"Processing: {input_path.name}")
    mark = marker_for(input_path)
    if mark.exists():
        log("Already processed; skipping")
        return True

    work_name = input_path.stem
    work_dir = ANALYSIS_DIR / work_name
    decompiled_dir = work_dir / "decompiled"
    jadx_dir = work_dir / "jadx_output"
    curl_out = work_dir / "curl.txt"
    ai_out = work_dir / "ai_analysis.txt"

    work_dir.mkdir(parents=True, exist_ok=True)

    apk_path: Optional[Path] = None
    temp_dir = ANALYSIS_DIR / ".tmp"
    temp_dir.mkdir(parents=True, exist_ok=True)

    try:
        if input_path.suffix.lower() == ".xapk":
            apk_path = find_base_apk(input_path, temp_dir)
            if not apk_path:
                log("Failed to obtain base APK from XAPK")
                return False
        else:
            apk_path = input_path

        if not decompile_with_apktool(apk_path, decompiled_dir):
            log("apktool decompile failed")
        if not decompile_with_jadx(apk_path, jadx_dir):
            log("jadx decompile failed")

        # Run basic endpoint extraction first
        src_root = jadx_dir if jadx_dir.exists() else decompiled_dir
        extract_endpoints(src_root, curl_out)
        
        # Run enhanced step-based analysis
        step_based_analysis(work_dir)

        mark.touch()
        log(f"Done -> {work_dir}")
        return True
    finally:
        # Do not delete temp_dir to allow inspection; could be cleaned by a separate task
        pass


def scan_inputs() -> list[Path]:
    files = []
    for pattern in ("*.apk", "*.xapk"):
        files.extend(DATA_DIR.glob(pattern))
    return sorted(files)


def process_once() -> None:
    for f in scan_inputs():
        process_file(f)


def watch_loop(interval: float = 5.0) -> None:
    log("Watching for new APK/XAPK in ./data ...")
    seen = {p.name for p in scan_inputs()}
    while True:
        time.sleep(interval)
        current = scan_inputs()
        current_names = {p.name for p in current}
        # New files
        for p in current:
            if p.name not in seen:
                process_file(p)
        # Also attempt processing existing but unprocessed files
        for p in current:
            if not marker_for(p).exists():
                process_file(p)
        seen = current_names


def main() -> int:
    parser = argparse.ArgumentParser()
    g = parser.add_mutually_exclusive_group()
    g.add_argument("--once", action="store_true", help="Process pending files once and exit")
    g.add_argument("--watch", action="store_true", help="Watch directory and process continuously")
    args = parser.parse_args()

    DATA_DIR.mkdir(exist_ok=True)
    ANALYSIS_DIR.mkdir(exist_ok=True)

    if args.watch:
        watch_loop()
    else:
        process_once()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
