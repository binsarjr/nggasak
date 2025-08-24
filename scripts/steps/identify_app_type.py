#!/usr/bin/env python3
"""
Step 1: App Type Identification

Identifies the technology stack used to build the Android app by analyzing
the decompiled files and folder structure.
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

class AppTypeIdentifier:
    """Identifies the technology stack of a decompiled Android app."""
    
    def __init__(self, decompiled_root: Path, jadx_root: Path):
        self.decompiled_root = decompiled_root
        self.jadx_root = jadx_root
        self.analysis_results = {}
    
    def identify(self) -> Dict[str, Any]:
        """
        Main identification method.
        Returns a dict with app_type, confidence, evidence, and reasoning.
        """
        # Check for each app type
        native_score = self._check_native_android()
        flutter_score = self._check_flutter()
        react_native_score = self._check_react_native()
        xamarin_score = self._check_xamarin()
        cordova_score = self._check_cordova()
        unity_score = self._check_unity()
        
        scores = {
            "Native Android": native_score,
            "Flutter": flutter_score,
            "React Native": react_native_score,
            "Xamarin": xamarin_score,
            "Cordova": cordova_score,
            "Unity": unity_score
        }
        
        # Determine the highest scoring type
        best_type = max(scores.keys(), key=lambda k: scores[k]['score'])
        best_score = scores[best_type]
        
        # Determine confidence level
        confidence = self._calculate_confidence(best_score['score'], best_score['evidence'])
        
        return {
            "app_type": best_type,
            "confidence": confidence,
            "evidence": best_score['evidence'],
            "reasoning": best_score['reasoning'],
            "all_scores": scores
        }
    
    def _check_native_android(self) -> Dict[str, Any]:
        """Check for Native Android (Java/Kotlin) indicators."""
        evidence = []
        score = 0
        
        # Check for smali files
        smali_dirs = list(self.decompiled_root.glob("smali*"))
        if smali_dirs:
            evidence.append(f"Found {len(smali_dirs)} smali directories")
            score += 30
        
        # Check for Java source in jadx output
        if self.jadx_root.exists():
            java_files = list(self.jadx_root.rglob("*.java"))
            if java_files:
                evidence.append(f"Found {len(java_files)} Java files in jadx output")
                score += 25
        
        # Check for Kotlin indicators
        kotlin_indicators = self._find_kotlin_indicators()
        if kotlin_indicators:
            evidence.extend(kotlin_indicators)
            score += 15
        
        # Check AndroidManifest for standard components
        manifest_components = self._check_standard_android_components()
        if manifest_components:
            evidence.extend(manifest_components)
            score += 10
        
        # Absence of cross-platform frameworks is positive for native
        if not self._has_cross_platform_indicators():
            evidence.append("No cross-platform framework indicators found")
            score += 20
        
        reasoning = "Native Android apps typically have smali bytecode, standard Android components, and lack cross-platform framework signatures."
        
        return {
            "score": score,
            "evidence": evidence,
            "reasoning": reasoning
        }
    
    def _check_flutter(self) -> Dict[str, Any]:
        """Check for Flutter indicators."""
        evidence = []
        score = 0
        
        # Check for flutter_assets directory
        flutter_assets = self.decompiled_root / "assets" / "flutter_assets"
        if flutter_assets.exists():
            evidence.append("Found flutter_assets/ directory")
            score += 40
            
            # Check for specific Flutter files
            if (flutter_assets / "AssetManifest.json").exists():
                evidence.append("Found AssetManifest.json")
                score += 15
            
            if (flutter_assets / "FontManifest.json").exists():
                evidence.append("Found FontManifest.json")
                score += 10
        
        # Check for libflutter.so
        lib_dirs = list(self.decompiled_root.glob("lib/*"))
        for lib_dir in lib_dirs:
            if (lib_dir / "libflutter.so").exists():
                evidence.append(f"Found libflutter.so in {lib_dir.name}")
                score += 30
                break
        
        # Check for Dart VM snapshots
        vm_snapshots = list(self.decompiled_root.rglob("*vm_snapshot*"))
        if vm_snapshots:
            evidence.append(f"Found {len(vm_snapshots)} VM snapshot files")
            score += 20
        
        # Check for Flutter package references
        flutter_packages = self._find_flutter_packages()
        if flutter_packages:
            evidence.extend(flutter_packages[:3])  # Limit to 3 examples
            score += 10
        
        reasoning = "Flutter apps contain flutter_assets/, libflutter.so, and Dart VM snapshots."
        
        return {
            "score": score,
            "evidence": evidence,
            "reasoning": reasoning
        }
    
    def _check_react_native(self) -> Dict[str, Any]:
        """Check for React Native indicators."""
        evidence = []
        score = 0
        
        # Check for JavaScript bundles
        js_bundles = []
        potential_bundles = [
            "assets/index.android.bundle",
            "assets/index.bundle", 
            "assets/main.jsbundle"
        ]
        
        for bundle_path in potential_bundles:
            full_path = self.decompiled_root / bundle_path
            if full_path.exists():
                evidence.append(f"Found JavaScript bundle: {bundle_path}")
                js_bundles.append(full_path)
                score += 35
        
        # Check for React Native signatures in bundles
        if js_bundles:
            rn_signatures = self._find_react_native_signatures(js_bundles[0])
            if rn_signatures:
                evidence.extend(rn_signatures[:2])
                score += 20
        
        # Check for React Native libraries
        rn_libs = list(self.decompiled_root.rglob("*react*native*"))
        if rn_libs:
            evidence.append(f"Found {len(rn_libs)} React Native library files")
            score += 15
        
        # Check for Hermes bytecode
        hermes_indicators = self._find_hermes_indicators()
        if hermes_indicators:
            evidence.extend(hermes_indicators)
            score += 10
        
        reasoning = "React Native apps contain JavaScript bundles and React Native runtime libraries."
        
        return {
            "score": score,
            "evidence": evidence,
            "reasoning": reasoning
        }
    
    def _check_xamarin(self) -> Dict[str, Any]:
        """Check for Xamarin indicators."""
        evidence = []
        score = 0
        
        # Check for Mono runtime
        mono_libs = list(self.decompiled_root.rglob("*mono*"))
        if mono_libs:
            evidence.append(f"Found {len(mono_libs)} Mono runtime files")
            score += 30
        
        # Check for .NET assemblies
        assemblies = list(self.decompiled_root.rglob("assemblies"))
        if assemblies:
            evidence.append("Found assemblies/ directory")
            score += 25
        
        # Check for Xamarin namespace references
        xamarin_refs = self._find_xamarin_references()
        if xamarin_refs:
            evidence.extend(xamarin_refs[:2])
            score += 15
        
        reasoning = "Xamarin apps contain Mono runtime and .NET assemblies."
        
        return {
            "score": score,
            "evidence": evidence,
            "reasoning": reasoning
        }
    
    def _check_cordova(self) -> Dict[str, Any]:
        """Check for Cordova/PhoneGap indicators."""
        evidence = []
        score = 0
        
        # Check for www directory
        www_dir = self.decompiled_root / "assets" / "www"
        if www_dir.exists():
            evidence.append("Found assets/www/ directory")
            score += 30
            
            # Check for cordova.js
            if (www_dir / "cordova.js").exists():
                evidence.append("Found cordova.js")
                score += 25
            
            # Check for HTML files
            html_files = list(www_dir.rglob("*.html"))
            if html_files:
                evidence.append(f"Found {len(html_files)} HTML files in www/")
                score += 15
        
        # Check for Cordova plugins
        cordova_plugins = self._find_cordova_plugins()
        if cordova_plugins:
            evidence.extend(cordova_plugins[:2])
            score += 10
        
        reasoning = "Cordova apps contain a www/ directory with HTML/JS content and cordova.js."
        
        return {
            "score": score,
            "evidence": evidence,
            "reasoning": reasoning
        }
    
    def _check_unity(self) -> Dict[str, Any]:
        """Check for Unity indicators."""
        evidence = []
        score = 0
        
        # Check for libunity.so
        unity_libs = list(self.decompiled_root.rglob("libunity.so"))
        if unity_libs:
            evidence.append("Found libunity.so")
            score += 40
        
        # Check for Unity asset bundles
        unity_assets = list(self.decompiled_root.rglob("*.unity3d"))
        if unity_assets:
            evidence.append(f"Found {len(unity_assets)} Unity asset bundles")
            score += 20
        
        # Check for Unity namespace references
        unity_refs = self._find_unity_references()
        if unity_refs:
            evidence.extend(unity_refs[:2])
            score += 15
        
        reasoning = "Unity apps contain libunity.so and Unity-specific asset files."
        
        return {
            "score": score,
            "evidence": evidence,
            "reasoning": reasoning
        }
    
    def _find_kotlin_indicators(self) -> List[str]:
        """Find Kotlin-specific indicators."""
        indicators = []
        
        # Check for kotlin directories in smali
        kotlin_dirs = list(self.decompiled_root.rglob("smali*/kotlin"))
        if kotlin_dirs:
            indicators.append(f"Found Kotlin bytecode in smali ({len(kotlin_dirs)} directories)")
        
        # Check for .kt file references (might be in jadx output)
        if self.jadx_root.exists():
            # Look for Kotlin-specific annotations or syntax
            try:
                result = subprocess.run(
                    ["grep", "-r", "kotlin", str(self.jadx_root)],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0 and result.stdout:
                    indicators.append("Found Kotlin references in decompiled code")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
        
        return indicators
    
    def _check_standard_android_components(self) -> List[str]:
        """Check AndroidManifest.xml for standard Android components."""
        components = []
        manifest_path = self.decompiled_root / "AndroidManifest.xml"
        
        if not manifest_path.exists():
            return components
        
        try:
            manifest_content = manifest_path.read_text(encoding="utf-8", errors="ignore")
            
            # Count activities, services, receivers
            activity_count = len(re.findall(r'<activity', manifest_content))
            service_count = len(re.findall(r'<service', manifest_content))
            receiver_count = len(re.findall(r'<receiver', manifest_content))
            
            if activity_count > 0:
                components.append(f"Found {activity_count} activities in manifest")
            if service_count > 0:
                components.append(f"Found {service_count} services in manifest")
            if receiver_count > 0:
                components.append(f"Found {receiver_count} broadcast receivers in manifest")
                
        except Exception:
            pass
        
        return components
    
    def _has_cross_platform_indicators(self) -> bool:
        """Check if there are any cross-platform framework indicators."""
        # Quick check for common cross-platform files/directories
        indicators = [
            "flutter_assets",
            "index.android.bundle",
            "libflutter.so",
            "assemblies",
            "assets/www",
            "libunity.so"
        ]
        
        for indicator in indicators:
            if list(self.decompiled_root.rglob(indicator)):
                return True
        
        return False
    
    def _find_flutter_packages(self) -> List[str]:
        """Find Flutter package references."""
        packages = []
        flutter_assets = self.decompiled_root / "assets" / "flutter_assets"
        
        if not flutter_assets.exists():
            return packages
        
        # Check packages directory
        packages_dir = flutter_assets / "packages"
        if packages_dir.exists():
            package_dirs = [d.name for d in packages_dir.iterdir() if d.is_dir()]
            if package_dirs:
                packages.append(f"Found Flutter packages: {', '.join(package_dirs[:5])}")
        
        return packages
    
    def _find_react_native_signatures(self, bundle_path: Path) -> List[str]:
        """Find React Native signatures in JavaScript bundle."""
        signatures = []
        
        try:
            # Read first 10KB of bundle to check for RN signatures
            with bundle_path.open('rb') as f:
                content = f.read(10240).decode('utf-8', errors='ignore')
            
            rn_patterns = [
                r'react-native',
                r'__reactNative',
                r'ReactNative',
                r'metro.*bundler',
                r'__DEV__.*react'
            ]
            
            for pattern in rn_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    signatures.append(f"Found React Native signature: {pattern}")
                    break  # Only report one signature per pattern type
                    
        except Exception:
            pass
        
        return signatures
    
    def _find_hermes_indicators(self) -> List[str]:
        """Find Hermes bytecode indicators."""
        indicators = []
        
        # Check for Hermes libraries
        hermes_libs = list(self.decompiled_root.rglob("*hermes*"))
        if hermes_libs:
            indicators.append(f"Found {len(hermes_libs)} Hermes-related files")
        
        return indicators
    
    def _find_xamarin_references(self) -> List[str]:
        """Find Xamarin-specific references."""
        references = []
        
        # Look for Xamarin-specific files
        xamarin_files = list(self.decompiled_root.rglob("*xamarin*"))
        if xamarin_files:
            references.append(f"Found {len(xamarin_files)} Xamarin-related files")
        
        return references
    
    def _find_cordova_plugins(self) -> List[str]:
        """Find Cordova plugin indicators."""
        plugins = []
        
        # Check for plugin-related files
        plugin_files = list(self.decompiled_root.rglob("*cordova*plugin*"))
        if plugin_files:
            plugins.append(f"Found {len(plugin_files)} Cordova plugin files")
        
        return plugins
    
    def _find_unity_references(self) -> List[str]:
        """Find Unity-specific references."""
        references = []
        
        # Look for Unity-specific files
        unity_files = list(self.decompiled_root.rglob("*unity*"))
        if unity_files:
            references.append(f"Found {len(unity_files)} Unity-related files")
        
        return references
    
    def _calculate_confidence(self, score: int, evidence: List[str]) -> str:
        """Calculate confidence level based on score and evidence quality."""
        if score >= 60 and len(evidence) >= 3:
            return "High"
        elif score >= 30 and len(evidence) >= 2:
            return "Medium"
        else:
            return "Low"


def identify_app_type(decompiled_root: Path, jadx_root: Path) -> Dict[str, Any]:
    """
    Convenience function to identify app type.
    
    Args:
        decompiled_root: Path to apktool decompiled directory
        jadx_root: Path to jadx output directory
        
    Returns:
        Dict with app_type, confidence, evidence, and reasoning
    """
    identifier = AppTypeIdentifier(decompiled_root, jadx_root)
    return identifier.identify()


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python identify_app_type.py <decompiled_root> <jadx_root>")
        sys.exit(1)
    
    decompiled_root = Path(sys.argv[1])
    jadx_root = Path(sys.argv[2])
    
    result = identify_app_type(decompiled_root, jadx_root)
    
    print(f"APP_TYPE: {result['app_type']}")
    print(f"CONFIDENCE: {result['confidence']}")
    print("EVIDENCE:")
    for evidence in result['evidence']:
        print(f"- {evidence}")
    print(f"\nREASONING:")
    print(result['reasoning'])
