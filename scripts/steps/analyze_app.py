#!/usr/bin/env python3
"""
Step 3: App Analysis

Performs the actual analysis based on the identified app type and selected tools.
Uses Claude API with appropriate prompts to extract endpoints and security information.
"""

import os
import subprocess
import sys
import select
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any


def run_claude_with_streaming(prompt: str, work_dir: Path, timeout: int = 300) -> Dict[str, Any]:
    """
    Run Claude with streaming output and proper error handling.
    
    Args:
        prompt: The prompt to send to Claude
        work_dir: Working directory for Claude execution
        timeout: Timeout in seconds (default 5 minutes)
        
    Returns:
        Dict with status, output, error, and metadata
    """
    # Check for Claude API key
    api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")
    if not api_key:
        return {
            "status": "error",
            "error": "Claude API key not configured",
            "output": "",
            "metadata": {"prompt_length": len(prompt), "duration": 0}
        }
    
    # Prepare environment
    env = dict(os.environ)
    env["ANTHROPIC_API_KEY"] = api_key
    base_url = os.environ.get("ANTHROPIC_BASE_URL")
    if base_url:
        env["ANTHROPIC_BASE_URL"] = base_url
    
    # Prepare command
    cmd = ["claude", "--dangerously-skip-permissions", "-p", prompt]
    
    print(f"[Claude] Executing Claude command...")
    print(f"[Claude] Prompt length: {len(prompt):,} characters")
    print(f"[Claude] Working directory: {work_dir}")
    print(f"[Claude] Timeout: {timeout} seconds")
    print("=" * 80)
    
    start_time = time.time()
    
    try:
        # Use Popen for streaming output
        process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line buffered
            universal_newlines=True,
            cwd=str(work_dir)
        )
        
        output_lines = []
        error_lines = []
        
        # Read output line by line with streaming display
        while True:
            # Check if process is still running
            if process.poll() is not None:
                break
            
            # Check for timeout
            elapsed = time.time() - start_time
            if elapsed > timeout:
                process.terminate()
                process.wait(timeout=10)  # Give it 10 seconds to terminate gracefully
                return {
                    "status": "timeout",
                    "error": f"Claude analysis timed out after {timeout} seconds",
                    "output": '\n'.join(output_lines),
                    "metadata": {"prompt_length": len(prompt), "duration": elapsed}
                }
            
            # Read available output
            try:
                ready, _, _ = select.select([process.stdout, process.stderr], [], [], 0.1)
                
                if process.stdout in ready:
                    line = process.stdout.readline()
                    if line:
                        line = line.rstrip('\n\r')
                        print(f"[Claude] {line}")
                        output_lines.append(line)
                        sys.stdout.flush()
                
                if process.stderr in ready:
                    line = process.stderr.readline()
                    if line:
                        line = line.rstrip('\n\r')
                        print(f"[Claude ERROR] {line}")
                        error_lines.append(line)
                        sys.stdout.flush()
                        
            except (OSError, select.error):
                # Fallback for systems without select (like Windows)
                # Read with a short timeout instead
                try:
                    line = process.stdout.readline()
                    if line:
                        line = line.rstrip('\n\r')
                        print(f"[Claude] {line}")
                        output_lines.append(line)
                        sys.stdout.flush()
                except:
                    pass
                break
        
        # Get any remaining output
        try:
            remaining_stdout, remaining_stderr = process.communicate(timeout=30)
            if remaining_stdout:
                for line in remaining_stdout.strip().split('\n'):
                    if line:
                        print(f"[Claude] {line}")
                        output_lines.append(line)
            
            if remaining_stderr:
                for line in remaining_stderr.strip().split('\n'):
                    if line:
                        print(f"[Claude ERROR] {line}")
                        error_lines.append(line)
        except subprocess.TimeoutExpired:
            process.kill()
            return {
                "status": "timeout",
                "error": "Process did not terminate gracefully",
                "output": '\n'.join(output_lines),
                "metadata": {"prompt_length": len(prompt), "duration": time.time() - start_time}
            }
        
        duration = time.time() - start_time
        
        print("=" * 80)
        print(f"[Claude] Analysis completed in {duration:.2f}s with return code: {process.returncode}")
        
        # Determine status and return result
        full_output = '\n'.join(output_lines)
        full_error = '\n'.join(error_lines)
        
        if process.returncode == 0:
            return {
                "status": "success",
                "output": full_output,
                "error": full_error,
                "metadata": {
                    "prompt_length": len(prompt),
                    "duration": duration,
                    "return_code": process.returncode
                }
            }
        else:
            return {
                "status": "error",
                "error": f"Claude failed with return code {process.returncode}: {full_error}",
                "output": full_output,
                "metadata": {
                    "prompt_length": len(prompt),
                    "duration": duration,
                    "return_code": process.returncode
                }
            }
            
    except FileNotFoundError:
        return {
            "status": "error",
            "error": "Claude CLI not found; install claude CLI tool",
            "output": "",
            "metadata": {"prompt_length": len(prompt), "duration": time.time() - start_time}
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Unexpected error running Claude: {e}",
            "output": "",
            "metadata": {"prompt_length": len(prompt), "duration": time.time() - start_time}
        }


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
        """Prepare minimal context information for Claude analysis."""
        context = {}
        
        # Only provide essential structure overview - let AI explore files as needed
        context["file_structure"] = self._get_file_structure_overview()
        
        # App type for reference
        context["app_type"] = self.app_type
        context["work_directory"] = str(self.work_dir)
        
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
        
        print(f"[AppAnalyzer] Running Claude analysis...")
        
        # Use the dedicated Claude function
        result = run_claude_with_streaming(full_prompt, self.work_dir, timeout=300)
        
        if result["status"] == "success":
            print(f"[AppAnalyzer] Claude analysis successful! Duration: {result['metadata']['duration']:.2f}s")
            return result["output"]
        else:
            print(f"[AppAnalyzer] Claude analysis failed: {result['error']}")
            return f"Claude analysis failed: {result['error']}"
    
    def _build_full_prompt(self, prompt_template: str, context: Dict[str, str]) -> str:
        """Build a concise prompt for agentic AI analysis."""
        full_prompt = f"""
{prompt_template}

=== TARGET INFO ===
App Type: {self.app_type}
Work Directory: {self.work_dir}

=== TASK ===
You are an agentic AI with tools to explore the codebase. Use your available tools to analyze this {self.app_type} app and find all real API endpoints. Create context for yourself as needed through tool usage.
"""
        
        return full_prompt
    

    
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
