#!/usr/bin/env python3
"""
Step 3: App Analysis

Performs the actual analysis based on the identified app type and selected tools.
Uses Claude API with appropriate prompts to extract endpoints and security information.
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any


class AppAnalyzer:
    """Analyzes the app using Claude API with appropriate prompts."""
    
    def __init__(self, work_dir: Path, app_type: str, confidence: str):
        self.work_dir = work_dir
        self.app_type = app_type
        self.confidence = confidence
        # Try to find prompts directory - works both in host and container
        current_file = Path(__file__).resolve()
        
        # Try different possible locations
        possible_prompts_paths = [
            Path("/prompts"),  # Container: /prompts (highest priority)
            Path.cwd() / "prompts",  # Current working directory
        ]
        
        # Add parent directory paths safely
        try:
            possible_prompts_paths.append(current_file.parents[2] / "prompts")
        except IndexError:
            pass
        try:
            possible_prompts_paths.append(current_file.parents[3] / "prompts")
        except IndexError:
            pass
        
        self.prompts_dir = None
        for path in possible_prompts_paths:
            if path.exists():
                self.prompts_dir = path
                break
        
        if self.prompts_dir is None:
            # Fallback - create a basic path
            self.prompts_dir = Path("/prompts")
        
    def analyze(self) -> Dict[str, Any]:
        """
        Perform comprehensive analysis based on app type.
        
        Returns:
            Dict with analysis results including endpoints, auth flows, etc.
        """
        try:
            print(f"[AppAnalyzer] Starting analysis for {self.app_type}")
            print(f"[AppAnalyzer] Using prompts directory: {self.prompts_dir}")
            print(f"[AppAnalyzer] Prompts directory exists: {self.prompts_dir.exists()}")
            
            # Prepare context for analysis
            print(f"[AppAnalyzer] Preparing analysis context...")
            context = self._prepare_analysis_context()
            print(f"[AppAnalyzer] Context prepared with {len(context)} items")
            
            # Select appropriate prompt
            print(f"[AppAnalyzer] Selecting prompt for {self.app_type}...")
            prompt_path = self._select_prompt()
            print(f"[AppAnalyzer] Selected prompt: {prompt_path}")
            print(f"[AppAnalyzer] Prompt file exists: {prompt_path.exists()}")
            
            if not prompt_path.exists():
                print(f"[AppAnalyzer] ERROR: Prompt file not found: {prompt_path}")
                return {
                    "app_type": self.app_type,
                    "confidence": self.confidence,
                    "analysis_context": context,
                    "raw_analysis": f"Error: Prompt file not found: {prompt_path}",
                    "processed_results": {"status": "failed", "error": "Prompt file not found", "endpoints_found": 0},
                    "curl_commands": [],
                    "security_findings": {}
                }
            
            # Run analysis with Claude
            print(f"[AppAnalyzer] Running Claude analysis...")
            analysis_result = self._run_claude_analysis(prompt_path, context)
            print(f"[AppAnalyzer] Claude analysis completed, result length: {len(str(analysis_result))}")
            
            # Post-process results
            print(f"[AppAnalyzer] Processing analysis results...")
            processed_results = self._process_analysis_results(analysis_result)
            print(f"[AppAnalyzer] Results processed: {processed_results.get('status', 'unknown')}")
            
            curl_commands = self._extract_curl_commands(analysis_result)
            security_findings = self._extract_security_findings(analysis_result)
            
            print(f"[AppAnalyzer] Analysis complete: {len(curl_commands)} curl commands, {len(security_findings)} security findings")
            
            return {
                "app_type": self.app_type,
                "confidence": self.confidence,
                "analysis_context": context,
                "raw_analysis": analysis_result,
                "processed_results": processed_results,
                "curl_commands": curl_commands,
                "security_findings": security_findings
            }
            
        except Exception as e:
            print(f"[AppAnalyzer] ERROR in analyze(): {e}")
            import traceback
            print(f"[AppAnalyzer] Traceback: {traceback.format_exc()}")
            
            # Return a safe fallback result
            return {
                "app_type": self.app_type,
                "confidence": self.confidence,
                "analysis_context": {},
                "raw_analysis": f"Error during analysis: {e}",
                "processed_results": {"status": "failed", "error": str(e), "endpoints_found": 0},
                "curl_commands": [],
                "security_findings": {}
            }
    
    def _prepare_analysis_context(self) -> Dict[str, str]:
        """Prepare context information for Claude analysis."""
        context = {}
        
        # Read AndroidManifest.xml
        manifest_path = self.work_dir / "decompiled" / "AndroidManifest.xml"
        if manifest_path.exists():
            try:
                context["manifest"] = manifest_path.read_text(encoding="utf-8", errors="ignore")[:8000]
            except Exception:
                context["manifest"] = "<unable to read>"
        else:
            context["manifest"] = "<not found>"
        
        # Read existing curl.txt if available
        curl_path = self.work_dir / "curl.txt"
        if curl_path.exists():
            try:
                context["existing_endpoints"] = curl_path.read_text(encoding="utf-8", errors="ignore")[:4000]
            except Exception:
                context["existing_endpoints"] = "<unable to read>"
        else:
            context["existing_endpoints"] = "<none found by extract_endpoints.py>"
        
        # Get file structure overview
        context["file_structure"] = self._get_file_structure_overview()
        
        # App-type specific context
        if self.app_type == "Flutter":
            context.update(self._get_flutter_context())
        elif self.app_type == "React Native":
            context.update(self._get_react_native_context())
        elif self.app_type == "Native Android":
            context.update(self._get_native_android_context())
        
        return context
    
    def _get_file_structure_overview(self) -> str:
        """Get an overview of the file structure."""
        structure_lines = []
        
        # Check decompiled directory
        decompiled_dir = self.work_dir / "decompiled"
        if decompiled_dir.exists():
            structure_lines.append("=== DECOMPILED STRUCTURE ===")
            structure_lines.extend(self._list_directory_summary(decompiled_dir, max_files=50))
        
        # Check jadx output directory
        jadx_dir = self.work_dir / "jadx_output"
        if jadx_dir.exists():
            structure_lines.append("\n=== JADX OUTPUT STRUCTURE ===")
            structure_lines.extend(self._list_directory_summary(jadx_dir, max_files=50))
        
        return "\n".join(structure_lines)
    
    def _list_directory_summary(self, directory: Path, max_files: int = 50) -> List[str]:
        """Get a summary of directory contents."""
        summary = []
        file_count = 0
        
        try:
            for item in sorted(directory.rglob("*")):
                if file_count >= max_files:
                    summary.append(f"... (truncated, showing first {max_files} files)")
                    break
                
                if item.is_file():
                    rel_path = item.relative_to(directory)
                    summary.append(str(rel_path))
                    file_count += 1
        except Exception:
            summary.append("<error reading directory>")
        
        return summary
    
    def _get_flutter_context(self) -> Dict[str, str]:
        """Get Flutter-specific context."""
        context = {}
        
        # Check flutter_assets
        flutter_assets = self.work_dir / "decompiled" / "assets" / "flutter_assets"
        if flutter_assets.exists():
            # Read AssetManifest.json
            asset_manifest = flutter_assets / "AssetManifest.json"
            if asset_manifest.exists():
                try:
                    context["asset_manifest"] = asset_manifest.read_text(encoding="utf-8", errors="ignore")[:2000]
                except Exception:
                    context["asset_manifest"] = "<unable to read>"
            
            # List flutter_assets contents
            context["flutter_assets_structure"] = self._list_directory_summary(flutter_assets, max_files=30)
        
        return context
    
    def _get_react_native_context(self) -> Dict[str, str]:
        """Get React Native-specific context."""
        context = {}
        
        # Check for JavaScript bundles
        assets_dir = self.work_dir / "decompiled" / "assets"
        if assets_dir.exists():
            bundle_files = []
            for pattern in ["*.bundle", "*.jsbundle"]:
                bundle_files.extend(assets_dir.glob(pattern))
            
            if bundle_files:
                # Read a sample from the first bundle
                try:
                    bundle_content = bundle_files[0].read_text(encoding="utf-8", errors="ignore")[:5000]
                    context["bundle_sample"] = bundle_content
                    context["bundle_info"] = f"Found bundles: {[b.name for b in bundle_files]}"
                except Exception:
                    context["bundle_sample"] = "<unable to read bundle>"
        
        return context
    
    def _get_native_android_context(self) -> Dict[str, str]:
        """Get Native Android-specific context."""
        context = {}
        
        # Check for key Java files in jadx output
        jadx_dir = self.work_dir / "jadx_output"
        if jadx_dir.exists():
            # Look for main activity or important classes
            java_files = list(jadx_dir.rglob("*.java"))
            if java_files:
                # Find MainActivity or similar
                main_files = [f for f in java_files if "main" in f.name.lower() or "activity" in f.name.lower()]
                if main_files:
                    try:
                        main_content = main_files[0].read_text(encoding="utf-8", errors="ignore")[:3000]
                        context["main_activity_sample"] = main_content
                    except Exception:
                        context["main_activity_sample"] = "<unable to read>"
        
        # Check strings.xml files
        strings_files = list(self.work_dir.rglob("strings.xml"))
        if strings_files:
            try:
                strings_content = strings_files[0].read_text(encoding="utf-8", errors="ignore")[:2000]
                context["strings_xml"] = strings_content
            except Exception:
                context["strings_xml"] = "<unable to read>"
        
        return context
    
    def _select_prompt(self) -> Path:
        """Select the appropriate analysis prompt based on app type."""
        prompt_mapping = {
            "Native Android": self.prompts_dir / "analysis" / "kotlin_analysis.md",
            "Flutter": self.prompts_dir / "analysis" / "flutter_analysis.md", 
            "React Native": self.prompts_dir / "analysis" / "react_native_analysis.md",
            "Xamarin": self.prompts_dir / "analysis" / "generic_analysis.md",
            "Cordova": self.prompts_dir / "analysis" / "generic_analysis.md",
            "Unity": self.prompts_dir / "analysis" / "generic_analysis.md"
        }
        
        selected_prompt = prompt_mapping.get(self.app_type, self.prompts_dir / "analysis" / "generic_analysis.md")
        
        if not selected_prompt.exists():
            # Fallback to generic analysis
            selected_prompt = self.prompts_dir / "analysis" / "generic_analysis.md"
        
        return selected_prompt
    
    def _run_claude_analysis(self, prompt_path: Path, context: Dict[str, str]) -> str:
        """Run Claude analysis with the selected prompt and context."""
        try:
            # Read the prompt template
            prompt_template = prompt_path.read_text(encoding="utf-8")
        except Exception as e:
            return f"Error reading prompt template: {e}"
        
        # Build the full prompt with context
        full_prompt = self._build_full_prompt(prompt_template, context)
        
        # Check for Claude API key
        api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")
        if not api_key:
            return "Claude API key not configured; skipping AI analysis"
        
        # Prepare environment
        env = dict(os.environ)
        env["ANTHROPIC_API_KEY"] = api_key
        base_url = os.environ.get("ANTHROPIC_BASE_URL")
        if base_url:
            env["ANTHROPIC_BASE_URL"] = base_url
        
        # Run Claude
        try:
            cmd = ["claude", "--dangerously-skip-permissions", full_prompt]
            result = subprocess.run(
                cmd, 
                env=env, 
                capture_output=True, 
                text=True, 
                timeout=300,  # 5 minute timeout
                check=False
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Claude analysis failed: {result.stderr}"
                
        except FileNotFoundError:
            return "Claude CLI not found; install claude CLI tool"
        except subprocess.TimeoutExpired:
            return "Claude analysis timed out after 5 minutes"
        except Exception as e:
            return f"Error running Claude analysis: {e}"
    
    def _build_full_prompt(self, prompt_template: str, context: Dict[str, str]) -> str:
        """Build the full prompt with context information."""
        context_section = self._format_context_section(context)
        
        full_prompt = f"""
{prompt_template}

=== ANALYSIS TARGET INFORMATION ===

App Type: {self.app_type} (Confidence: {self.confidence})
Analysis Directory: {self.work_dir}

{context_section}

=== YOUR TASK ===

Based on the app type ({self.app_type}) and the provided context, perform a thorough analysis to find all real API endpoints. Follow the specific strategies outlined in the prompt above for {self.app_type} apps.

Focus on:
1. Finding actual HTTP/HTTPS URLs
2. Deobfuscating any hidden or encoded URLs  
3. Understanding the authentication flow
4. Identifying sensitive data handling
5. Creating working curl commands

Provide your analysis in the format specified in the prompt.
"""
        
        return full_prompt
    
    def _format_context_section(self, context: Dict[str, str]) -> str:
        """Format the context information for the prompt."""
        sections = []
        
        if "manifest" in context:
            sections.append(f"=== ANDROID MANIFEST ===\n{context['manifest']}\n")
        
        if "existing_endpoints" in context:
            sections.append(f"=== EXISTING ENDPOINTS (from extract_endpoints.py) ===\n{context['existing_endpoints']}\n")
        
        if "file_structure" in context:
            sections.append(f"=== FILE STRUCTURE OVERVIEW ===\n{context['file_structure']}\n")
        
        # App-specific context
        if "asset_manifest" in context:
            sections.append(f"=== FLUTTER ASSET MANIFEST ===\n{context['asset_manifest']}\n")
        
        if "bundle_sample" in context:
            sections.append(f"=== REACT NATIVE BUNDLE SAMPLE ===\n{context['bundle_sample']}\n")
        
        if "main_activity_sample" in context:
            sections.append(f"=== MAIN ACTIVITY SAMPLE ===\n{context['main_activity_sample']}\n")
        
        if "strings_xml" in context:
            sections.append(f"=== STRINGS.XML SAMPLE ===\n{context['strings_xml']}\n")
        
        return "\n".join(sections)
    
    def _process_analysis_results(self, analysis_result: str) -> Dict[str, Any]:
        """Process and structure the Claude analysis results."""
        if not analysis_result or "Error" in analysis_result or "not found" in analysis_result:
            return {
                "status": "failed",
                "error": analysis_result,
                "endpoints_found": 0,
                "auth_flows": [],
                "security_issues": []
            }
        
        # Extract structured information from the analysis
        endpoints = self._extract_endpoints_from_analysis(analysis_result)
        auth_flows = self._extract_auth_flows(analysis_result)
        security_issues = self._extract_security_issues(analysis_result)
        
        return {
            "status": "success",
            "endpoints_found": len(endpoints),
            "endpoints": endpoints,
            "auth_flows": auth_flows,
            "security_issues": security_issues,
            "deobfuscation_methods": self._extract_deobfuscation_methods(analysis_result)
        }
    
    def _extract_endpoints_from_analysis(self, analysis: str) -> List[Dict[str, str]]:
        """Extract endpoint information from Claude analysis."""
        endpoints = []
        
        # Look for curl commands or HTTP URLs in the analysis
        import re
        
        # Find curl commands
        curl_pattern = r'curl\s+.*?(?=\n\n|\n#|\nHttp|\Z)'
        curl_matches = re.findall(curl_pattern, analysis, re.DOTALL | re.MULTILINE)
        
        for match in curl_matches:
            # Extract URL from curl command
            url_pattern = r'"(https?://[^"]+)"'
            url_match = re.search(url_pattern, match)
            if url_match:
                endpoints.append({
                    "url": url_match.group(1),
                    "curl_command": match.strip(),
                    "source": "claude_analysis"
                })
        
        # Also look for standalone URLs
        url_pattern = r'https?://[^\s<>"\'{}|\\^`\[\]]+[^\s.,<>"\'{}|\\^`\[\]]'
        url_matches = re.findall(url_pattern, analysis)
        
        for url in url_matches:
            if not any(ep["url"] == url for ep in endpoints):
                endpoints.append({
                    "url": url,
                    "curl_command": f"curl -X GET \"{url}\"",
                    "source": "claude_analysis_url"
                })
        
        return endpoints
    
    def _extract_auth_flows(self, analysis: str) -> List[str]:
        """Extract authentication flow information."""
        auth_flows = []
        
        # Look for auth-related patterns in the analysis
        auth_patterns = [
            r'auth.*flow.*?(?=\n\n|\n[A-Z]|\Z)',
            r'login.*process.*?(?=\n\n|\n[A-Z]|\Z)', 
            r'token.*authentication.*?(?=\n\n|\n[A-Z]|\Z)'
        ]
        
        import re
        for pattern in auth_patterns:
            matches = re.findall(pattern, analysis, re.DOTALL | re.IGNORECASE)
            auth_flows.extend([match.strip() for match in matches])
        
        return auth_flows
    
    def _extract_security_issues(self, analysis: str) -> List[str]:
        """Extract security issues from the analysis."""
        security_issues = []
        
        # Look for security-related patterns
        security_patterns = [
            r'security.*issue.*?(?=\n\n|\n[A-Z]|\Z)',
            r'vulnerability.*?(?=\n\n|\n[A-Z]|\Z)',
            r'hardcoded.*credential.*?(?=\n\n|\n[A-Z]|\Z)',
            r'insecure.*?(?=\n\n|\n[A-Z]|\Z)'
        ]
        
        import re
        for pattern in security_patterns:
            matches = re.findall(pattern, analysis, re.DOTALL | re.IGNORECASE)
            security_issues.extend([match.strip() for match in matches])
        
        return security_issues
    
    def _extract_deobfuscation_methods(self, analysis: str) -> List[str]:
        """Extract deobfuscation methods used."""
        methods = []
        
        # Look for deobfuscation mentions
        if "base64" in analysis.lower():
            methods.append("Base64 decoding")
        if "decrypt" in analysis.lower():
            methods.append("Decryption")
        if "concat" in analysis.lower() or "build" in analysis.lower():
            methods.append("String concatenation reversal")
        
        return methods
    
    def _extract_curl_commands(self, analysis: str) -> List[str]:
        """Extract curl commands from the analysis."""
        import re
        
        # Find all curl commands
        curl_pattern = r'curl\s+.*?(?=\n\n|\n#|\ncurl|\Z)'
        curl_commands = re.findall(curl_pattern, analysis, re.DOTALL | re.MULTILINE)
        
        return [cmd.strip() for cmd in curl_commands if cmd.strip()]
    
    def _extract_security_findings(self, analysis: str) -> Dict[str, List[str]]:
        """Extract security findings organized by category."""
        findings = {
            "credentials": [],
            "encryption": [],
            "network_security": [],
            "permissions": [],
            "obfuscation": []
        }
        
        # This would be enhanced to properly parse Claude's security analysis
        # For now, return a basic structure
        
        return findings


def analyze_app(work_dir: Path, app_type: str, confidence: str = "Medium") -> Dict[str, Any]:
    """
    Convenience function to analyze an app.
    
    Args:
        work_dir: Path to the analysis working directory
        app_type: Identified app type
        confidence: Confidence level of identification
        
    Returns:
        Dict with comprehensive analysis results
    """
    analyzer = AppAnalyzer(work_dir, app_type, confidence)
    return analyzer.analyze()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python analyze_app.py <work_dir> <app_type> [confidence]")
        sys.exit(1)
    
    work_dir = Path(sys.argv[1])
    app_type = sys.argv[2]
    confidence = sys.argv[3] if len(sys.argv) > 3 else "Medium"
    
    if not work_dir.exists():
        print(f"Error: Work directory {work_dir} does not exist")
        sys.exit(1)
    
    print(f"Analyzing {app_type} app in {work_dir}...")
    
    result = analyze_app(work_dir, app_type, confidence)
    
    print(f"Analysis Status: {result['processed_results']['status']}")
    print(f"Endpoints Found: {result['processed_results']['endpoints_found']}")
    
    if result['curl_commands']:
        print(f"\nCurl Commands ({len(result['curl_commands'])}):")
        for cmd in result['curl_commands'][:5]:  # Show first 5
            print(f"- {cmd}")
    
    print(f"\nDetailed results saved in analysis output.")
