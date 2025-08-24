#!/usr/bin/env python3
"""
Step Runner - Orchestrates the 3-step analysis pipeline

Coordinates the execution of:
1. App Type Identification
2. Tool Selection  
3. App Analysis

This replaces the simple AI analysis in the original auto_queue.py with
a structured, step-based approach using specialized prompts.
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

# Import our step modules
from steps.identify_app_type import identify_app_type
from steps.select_tools import select_tools_for_app
from steps.analyze_app import analyze_app


class StepRunner:
    """Orchestrates the 3-step analysis pipeline."""
    
    def __init__(self, work_dir: Path):
        self.work_dir = work_dir
        self.decompiled_dir = work_dir / "decompiled"
        self.jadx_dir = work_dir / "jadx_output"
        self.results = {}
        
    def run_pipeline(self) -> Dict[str, Any]:
        """
        Run the complete 3-step analysis pipeline.
        
        Returns:
            Dict containing results from all steps
        """
        print(f"[StepRunner] Starting 3-step analysis pipeline for {self.work_dir.name}")
        
        # Step 1: Identify App Type
        step1_result = self._run_step_1_identification()
        if not step1_result:
            return {"error": "Step 1 (App Identification) failed"}
        
        # Step 2: Select Tools
        step2_result = self._run_step_2_tool_selection(step1_result)
        if not step2_result:
            return {"error": "Step 2 (Tool Selection) failed"}
        
        # Step 3: Analyze App
        step3_result = self._run_step_3_analysis(step1_result, step2_result)
        if not step3_result:
            return {"error": "Step 3 (App Analysis) failed"}
        
        # Combine all results
        pipeline_result = {
            "pipeline_status": "completed",
            "app_identification": step1_result,
            "tool_selection": step2_result,
            "app_analysis": step3_result,
            "summary": self._create_pipeline_summary(step1_result, step2_result, step3_result)
        }
        
        # Save comprehensive results
        self._save_pipeline_results(pipeline_result)
        
        print(f"[StepRunner] Pipeline completed successfully")
        return pipeline_result
    
    def _run_step_1_identification(self) -> Optional[Dict[str, Any]]:
        """Run Step 1: App Type Identification."""
        print("[Step 1] Identifying app type...")
        
        if not self.decompiled_dir.exists():
            print(f"[Step 1] Error: Decompiled directory not found: {self.decompiled_dir}")
            return None
        
        try:
            start_time = time.time()
            result = identify_app_type(self.decompiled_dir, self.jadx_dir)
            duration = time.time() - start_time
            
            print(f"[Step 1] Identified as: {result['app_type']} (Confidence: {result['confidence']})")
            print(f"[Step 1] Evidence: {len(result['evidence'])} items found")
            print(f"[Step 1] Completed in {duration:.2f}s")
            
            # Save step 1 results
            step1_file = self.work_dir / "step1_identification.json"
            with step1_file.open('w') as f:
                json.dump(result, f, indent=2)
            
            return result
            
        except Exception as e:
            print(f"[Step 1] Error during app identification: {e}")
            return None
    
    def _run_step_2_tool_selection(self, step1_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Run Step 2: Tool Selection."""
        print("[Step 2] Selecting analysis tools...")
        
        app_type = step1_result['app_type']
        confidence = step1_result['confidence']
        
        try:
            start_time = time.time()
            result = select_tools_for_app(app_type, confidence)
            duration = time.time() - start_time
            
            primary_tool_count = len(result['primary_tools'])
            fallback_tool_count = len(result['fallback_tools'])
            
            print(f"[Step 2] Selected {primary_tool_count} primary tools and {fallback_tool_count} fallback tools")
            print(f"[Step 2] Analysis strategy: {len(result['analysis_strategy']['phases'])} phases")
            print(f"[Step 2] Completed in {duration:.2f}s")
            
            # Save step 2 results
            step2_file = self.work_dir / "step2_tool_selection.json"
            with step2_file.open('w') as f:
                json.dump(result, f, indent=2)
            
            return result
            
        except Exception as e:
            print(f"[Step 2] Error during tool selection: {e}")
            return None
    
    def _run_step_3_analysis(self, step1_result: Dict[str, Any], step2_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Run Step 3: App Analysis."""
        print("[Step 3] Performing detailed app analysis...")
        
        app_type = step1_result['app_type']
        confidence = step1_result['confidence']
        
        try:
            start_time = time.time()
            result = analyze_app(self.work_dir, app_type, confidence)
            duration = time.time() - start_time
            
            # Debug: Print result structure
            print(f"[Step 3] DEBUG: Result keys: {list(result.keys())}")
            
            # Safe access to nested dict
            processed_results = result.get('processed_results', {})
            endpoints_found = processed_results.get('endpoints_found', 0)
            curl_commands = result.get('curl_commands', [])
            analysis_status = processed_results.get('status', 'unknown')
            
            print(f"[Step 3] Found {endpoints_found} endpoints")
            print(f"[Step 3] Generated {len(curl_commands)} curl commands")
            print(f"[Step 3] Analysis status: {analysis_status}")
            print(f"[Step 3] Completed in {duration:.2f}s")
            
            # Save step 3 results
            step3_file = self.work_dir / "step3_analysis.json"
            with step3_file.open('w') as f:
                json.dump(result, f, indent=2)
            
            # Also update the curl.txt file with new findings
            self._update_curl_file(curl_commands)
            
            return result
            
        except Exception as e:
            print(f"[Step 3] Error during app analysis: {e}")
            print(f"[Step 3] Error type: {type(e).__name__}")
            import traceback
            print(f"[Step 3] Traceback: {traceback.format_exc()}")
            return None
    
    def _update_curl_file(self, curl_commands: list):
        """Update curl.txt with analysis results."""
        curl_file = self.work_dir / "curl.txt"
        
        try:
            # Read existing content
            existing_content = ""
            if curl_file.exists():
                existing_content = curl_file.read_text(encoding="utf-8")
            
            # Add new findings
            with curl_file.open('w', encoding="utf-8") as f:
                f.write("# Enhanced curl.txt - Generated by Step-based Analysis Pipeline\n")
                f.write(f"# Analysis Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                if existing_content and not existing_content.startswith("#"):
                    f.write("# === ORIGINAL FINDINGS (from extract_endpoints.py) ===\n")
                    f.write(existing_content)
                    f.write("\n\n")
                
                if curl_commands:
                    f.write("# === ENHANCED FINDINGS (from Claude Analysis) ===\n")
                    for cmd in curl_commands:
                        f.write(f"{cmd}\n\n")
                else:
                    f.write("# No additional endpoints found by Claude analysis\n")
                    
        except Exception as e:
            print(f"[Step 3] Warning: Could not update curl.txt: {e}")
    
    def _create_pipeline_summary(self, step1: Dict, step2: Dict, step3: Dict) -> Dict[str, Any]:
        """Create a summary of the pipeline execution."""
        return {
            "app_type": step1['app_type'],
            "confidence": step1['confidence'],
            "evidence_count": len(step1['evidence']),
            "tools_selected": len(step2['primary_tools']),
            "analysis_phases": len(step2['analysis_strategy']['phases']),
            "endpoints_found": step3['processed_results']['endpoints_found'],
            "curl_commands_generated": len(step3['curl_commands']),
            "analysis_status": step3['processed_results']['status'],
            "recommended_next_steps": self._generate_next_steps(step1, step2, step3)
        }
    
    def _generate_next_steps(self, step1: Dict, step2: Dict, step3: Dict) -> list:
        """Generate recommended next steps based on analysis results."""
        next_steps = []
        
        app_type = step1['app_type']
        confidence = step1['confidence']
        endpoints_found = step3['processed_results']['endpoints_found']
        
        # Confidence-based recommendations
        if confidence == "Low":
            next_steps.append("Re-run analysis with manual app type specification")
            next_steps.append("Try additional decompilation tools")
        
        # App-type specific recommendations
        if app_type == "Flutter" and endpoints_found == 0:
            next_steps.append("Use reFlutter for dynamic analysis")
            next_steps.append("Analyze Dart VM snapshots with specialized tools")
        elif app_type == "React Native" and endpoints_found == 0:
            next_steps.append("Extract and beautify JavaScript bundles manually")
            next_steps.append("Check for Hermes bytecode compilation")
        elif app_type == "Native Android":
            next_steps.append("Perform dynamic analysis with Frida")
            next_steps.append("Check for runtime URL construction")
        
        # General recommendations
        if endpoints_found == 0:
            next_steps.append("Perform network traffic analysis")
            next_steps.append("Check for encrypted or heavily obfuscated endpoints")
        else:
            next_steps.append("Test discovered endpoints with authentication")
            next_steps.append("Perform parameter fuzzing on discovered APIs")
        
        return next_steps
    
    def _save_pipeline_results(self, results: Dict[str, Any]):
        """Save comprehensive pipeline results."""
        # Save main results file
        results_file = self.work_dir / "pipeline_results.json"
        with results_file.open('w') as f:
            json.dump(results, f, indent=2)
        
        # Save human-readable summary
        summary_file = self.work_dir / "analysis_summary.txt"
        with summary_file.open('w') as f:
            self._write_human_readable_summary(f, results)
    
    def _write_human_readable_summary(self, file, results: Dict[str, Any]):
        """Write a human-readable summary of the analysis."""
        summary = results['summary']
        
        file.write("=== STEP-BASED ANALYSIS SUMMARY ===\n\n")
        file.write(f"App Type: {summary['app_type']} (Confidence: {summary['confidence']})\n")
        file.write(f"Evidence Points: {summary['evidence_count']}\n")
        file.write(f"Tools Selected: {summary['tools_selected']}\n")
        file.write(f"Analysis Phases: {summary['analysis_phases']}\n")
        file.write(f"Endpoints Found: {summary['endpoints_found']}\n")
        file.write(f"Curl Commands: {summary['curl_commands_generated']}\n")
        file.write(f"Analysis Status: {summary['analysis_status']}\n\n")
        
        # Evidence from Step 1
        file.write("=== IDENTIFICATION EVIDENCE ===\n")
        for evidence in results['app_identification']['evidence']:
            file.write(f"- {evidence}\n")
        file.write(f"\nReasoning: {results['app_identification']['reasoning']}\n\n")
        
        # Analysis Strategy from Step 2
        file.write("=== ANALYSIS STRATEGY ===\n")
        for phase in results['tool_selection']['analysis_strategy']['phases']:
            file.write(f"Phase: {phase['name']}\n")
            file.write(f"  Description: {phase['description']}\n")
            file.write(f"  Focus: {', '.join(phase['focus'])}\n\n")
        
        # Key Findings from Step 3
        file.write("=== KEY FINDINGS ===\n")
        if results['app_analysis']['curl_commands']:
            file.write("Discovered Endpoints:\n")
            for cmd in results['app_analysis']['curl_commands']:
                file.write(f"  {cmd}\n")
        else:
            file.write("No endpoints discovered through automated analysis.\n")
        
        file.write(f"\n=== RECOMMENDED NEXT STEPS ===\n")
        for step in summary['recommended_next_steps']:
            file.write(f"- {step}\n")


def run_step_based_analysis(work_dir: Path) -> Dict[str, Any]:
    """
    Convenience function to run the complete step-based analysis.
    
    Args:
        work_dir: Path to the analysis working directory
        
    Returns:
        Dict with comprehensive pipeline results
    """
    runner = StepRunner(work_dir)
    return runner.run_pipeline()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python step_runner.py <work_directory>")
        print("Example: python step_runner.py ../analysis/myapp")
        sys.exit(1)
    
    work_dir = Path(sys.argv[1])
    
    if not work_dir.exists():
        print(f"Error: Work directory {work_dir} does not exist")
        sys.exit(1)
    
    if not (work_dir / "decompiled").exists():
        print(f"Error: No decompiled directory found in {work_dir}")
        print("Make sure to run apktool decompilation first")
        sys.exit(1)
    
    print(f"Starting step-based analysis for: {work_dir}")
    
    try:
        results = run_step_based_analysis(work_dir)
        
        if "error" in results:
            print(f"Pipeline failed: {results['error']}")
            sys.exit(1)
        else:
            print("Pipeline completed successfully!")
            print(f"Results saved in: {work_dir}/pipeline_results.json")
            print(f"Summary available at: {work_dir}/analysis_summary.txt")
            
    except Exception as e:
        print(f"Pipeline execution failed: {e}")
        sys.exit(1)
