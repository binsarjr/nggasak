#!/usr/bin/env python3
"""
Nggasak Endpoint Extractor

Scan decompiled APK sources to extract real API endpoints and generate a draft
analysis/curl.txt with usable curl templates. Works best after:
  - apktool d app.apk -o decompiled/
  - jadx app.apk -d jadx_output/

Usage:
    python3 scripts/extract_endpoints.py --root ./data/decompiled --out ./analysis/curl.txt

No external dependencies; stdlib only.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, List, Optional, Set, Tuple


URL_REGEX = re.compile(r"https?://[\w\-._~:/?#\[\]@!$&'()*+,;=%]+")
RETROFIT_ANNOTATION_REGEX = re.compile(r"@(?:GET|POST|PUT|PATCH|DELETE|HEAD)\(\s*\"([^\"]+)\"\s*\)")
RETROFIT_BASEURL_REGEX = re.compile(r"baseUrl\(\s*\"([^\"]+)\"\s*\)")

# Base64-ish strings that could contain URLs.
BASE64_CANDIDATE_REGEX = re.compile(r"\b[A-Za-z0-9+/]{16,}={0,2}\b")

TEXT_EXTS = {
    ".java", ".kt", ".smali", ".xml", ".json", ".properties", ".txt",
    ".js", ".ts", ".jsx", ".tsx", ".dart", ".cfg", ".ini", ".gradle",
}


@dataclass(frozen=True)
class Finding:
    url: str
    source_file: str
    line_no: int
    note: str = ""


def iter_files(root: Path) -> Iterator[Path]:
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in TEXT_EXTS:
            yield p


def safe_read_text(path: Path) -> Optional[str]:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None


def find_urls_in_text(text: str) -> List[Tuple[str, int]]:
    urls: List[Tuple[str, int]] = []
    for i, line in enumerate(text.splitlines(), start=1):
        for m in URL_REGEX.finditer(line):
            urls.append((m.group(0), i))
    return urls


def try_decode_base64(s: str) -> Optional[str]:
    # Fast reject if not plausible
    if len(s) % 4 != 0:
        # Often base64 is not padded; try adding padding heuristically
        padding = (4 - (len(s) % 4)) % 4
        s = s + ("=" * padding)
    try:
        raw = base64.b64decode(s, validate=False)
    except binascii.Error:
        return None
    decoded = raw.decode("utf-8", errors="ignore")
    if "http://" in decoded or "https://" in decoded:
        return decoded
    return None


def find_obfuscated_urls(text: str) -> List[Tuple[str, int, str]]:
    findings: List[Tuple[str, int, str]] = []
    for i, line in enumerate(text.splitlines(), start=1):
        for m in BASE64_CANDIDATE_REGEX.finditer(line):
            candidate = m.group(0)
            decoded = try_decode_base64(candidate)
            if decoded:
                # Extract any URLs from decoded content
                for m2 in URL_REGEX.finditer(decoded):
                    findings.append((m2.group(0), i, f"base64:{candidate[:16]}…"))
    return findings


def find_retrofit_paths(text: str) -> Tuple[Set[str], Set[str]]:
    base_urls: Set[str] = set(RETROFIT_BASEURL_REGEX.findall(text))
    paths: Set[str] = set(RETROFIT_ANNOTATION_REGEX.findall(text))
    return base_urls, paths


def normalize_url(url: str) -> str:
    # Drop trivial trailing punctuation
    return url.rstrip("\"');, ]}")


def combine_base_and_paths(base_urls: Iterable[str], paths: Iterable[str]) -> Set[str]:
    out: Set[str] = set()
    for b in base_urls:
        b_norm = normalize_url(b)
        for p in paths:
            if p.startswith("http://") or p.startswith("https://"):
                out.add(normalize_url(p))
            else:
                # Combine smartly
                if not b_norm.endswith("/") and not p.startswith("/"):
                    out.add(b_norm + "/" + p)
                elif b_norm.endswith("/") and p.startswith("/"):
                    out.add(b_norm + p.lstrip("/"))
                else:
                    out.add(b_norm + p)
    return out


def collect_findings(root: Path) -> List[Finding]:
    findings: List[Finding] = []
    seen: Set[str] = set()
    for path in iter_files(root):
        text = safe_read_text(path)
        if text is None:
            continue

        # Direct URLs
        for url, ln in find_urls_in_text(text):
            url = normalize_url(url)
            if url not in seen:
                findings.append(Finding(url, str(path), ln, note="direct"))
                seen.add(url)

        # Obfuscated URLs (base64)
        for url, ln, note in find_obfuscated_urls(text):
            url = normalize_url(url)
            if url not in seen:
                findings.append(Finding(url, str(path), ln, note=note))
                seen.add(url)

        # Retrofit-annotated paths + baseUrl
        base_urls, paths = find_retrofit_paths(text)
        if base_urls and paths:
            for u in combine_base_and_paths(base_urls, paths):
                if u not in seen:
                    findings.append(Finding(u, str(path), 1, note="retrofit"))
                    seen.add(u)

    return findings


def write_curl(findings: List[Finding], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        f.write("# Auto-generated by scripts/extract_endpoints.py\n")
        f.write("# Review, deduplicate logically related endpoints, and fill auth headers.\n\n")
        for idx, item in enumerate(sorted(findings, key=lambda x: (x.url, x.source_file)) , start=1):
            f.write(f"# {idx}. Source: {item.source_file}:{item.line_no} ({item.note})\n")
            method = "GET"
            # Heuristic: guess method by path keywords
            low = item.url.lower()
            if any(k in low for k in ["/login", "/auth", "/token", "/signup", "/register"]):
                method = "POST"
            f.write(f"curl -X {method} \"{item.url}\" \\\n")
            if method == "POST":
                f.write("  -H \"Content-Type: application/json\" \\\n")
                f.write("  -d '{\"example\":\"payload\"}' \\\n")
            f.write("  -H \"Authorization: Bearer [TOKEN]\"\n\n")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Extract API endpoints from code")
    parser.add_argument("--root", default="./data/decompiled", help="Root folder to scan (default: ./data/decompiled)")
    parser.add_argument("--out", default="./analysis/curl.txt", help="Output curl file (default: ./analysis/curl.txt)")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"[!] Root path not found: {root}", file=sys.stderr)
        return 2

    findings = collect_findings(root)
    if not findings:
        print("[i] No endpoints found. Try providing different root (e.g., ./jadx_output)")
    write_curl(findings, Path(args.out).resolve())
    print(f"[+] Wrote {len(findings)} endpoints to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
