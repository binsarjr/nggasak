#!/usr/bin/env python3
"""
Step 2: Tool Selection

Selects the appropriate analysis tools based on the identified app type.
Returns a list of tools and their configurations for the specific technology stack.
"""

from pathlib import Path
from typing import Dict, List, Tuple, Any


class ToolSelector:
    """Selects appropriate analysis tools based on app type."""
    
    def __init__(self):
        self.tool_configs = self._initialize_tool_configs()
    
    def select_tools(self, app_type: str, confidence: str) -> Dict[str, Any]:
        """
        Select tools based on app type and confidence level.
        
        Args:
            app_type: The identified app type (e.g., "Native Android", "Flutter")
            confidence: Confidence level ("High", "Medium", "Low")
            
        Returns:
            Dict containing primary tools, fallback tools, and analysis strategy
        """
        primary_tools = self._get_primary_tools(app_type)
        fallback_tools = self._get_fallback_tools(app_type, confidence)
        analysis_strategy = self._get_analysis_strategy(app_type)
        
        return {
            "app_type": app_type,
            "confidence": confidence,
            "primary_tools": primary_tools,
            "fallback_tools": fallback_tools,
            "analysis_strategy": analysis_strategy,
            "tool_commands": self._get_tool_commands(app_type),
            "expected_artifacts": self._get_expected_artifacts(app_type)
        }
    
    def _initialize_tool_configs(self) -> Dict[str, Dict]:
        """Initialize tool configurations for each app type."""
        return {
            "Native Android": {
                "primary": ["jadx", "apktool", "strings"],
                "secondary": ["dex2jar", "jd-gui", "aapt"],
                "dynamic": ["frida", "objection"],
                "specialized": ["mobsf", "classyshark"]
            },
            "Flutter": {
                "primary": ["jadx", "apktool", "reFlutter", "blutter"],
                "secondary": ["dart_analyzer", "flutter_tools"],
                "dynamic": ["frida", "reFlutter"],
                "specialized": ["doldrums", "snapshot_analyzer"]
            },
            "React Native": {
                "primary": ["jadx", "apktool", "js-beautify"],
                "secondary": ["hermes-dec", "metro-symbolicate"],
                "dynamic": ["frida", "flipper", "reactotron"],
                "specialized": ["react-native-decompiler"]
            },
            "Xamarin": {
                "primary": ["jadx", "apktool", "ildasm"],
                "secondary": ["dotnet-decompiler", "reflexil"],
                "dynamic": ["frida"],
                "specialized": ["xamarin-analyzer"]
            },
            "Cordova": {
                "primary": ["jadx", "apktool"],
                "secondary": ["js-beautify", "html-analyzer"],
                "dynamic": ["frida", "chrome-devtools"],
                "specialized": ["cordova-analyzer"]
            },
            "Unity": {
                "primary": ["jadx", "apktool", "unity-studio"],
                "secondary": ["il2cpp-dumper", "unity-assets-extractor"],
                "dynamic": ["frida", "cheat-engine"],
                "specialized": ["unity-analyzer", "asset-bundle-extractor"]
            }
        }
    
    def _get_primary_tools(self, app_type: str) -> List[Dict[str, Any]]:
        """Get primary tools for the app type."""
        if app_type not in self.tool_configs:
            app_type = "Native Android"  # Default fallback
        
        config = self.tool_configs[app_type]
        tools = []
        
        for tool_name in config["primary"]:
            tool_info = self._get_tool_info(tool_name, app_type)
            if tool_info:
                tools.append(tool_info)
        
        return tools
    
    def _get_fallback_tools(self, app_type: str, confidence: str) -> List[Dict[str, Any]]:
        """Get fallback tools based on confidence level."""
        if app_type not in self.tool_configs:
            app_type = "Native Android"
            
        config = self.tool_configs[app_type]
        tools = []
        
        # If confidence is low, include more tools
        if confidence == "Low":
            # Include tools from multiple categories
            for tool_name in config.get("secondary", []) + config.get("specialized", []):
                tool_info = self._get_tool_info(tool_name, app_type)
                if tool_info:
                    tools.append(tool_info)
        else:
            # Just include secondary tools
            for tool_name in config.get("secondary", []):
                tool_info = self._get_tool_info(tool_name, app_type)
                if tool_info:
                    tools.append(tool_info)
        
        return tools
    
    def _get_tool_info(self, tool_name: str, app_type: str) -> Dict[str, Any]:
        """Get detailed information about a specific tool."""
        tool_definitions = {
            # Universal tools
            "jadx": {
                "name": "jadx",
                "description": "Java decompiler for Android APKs",
                "command": "jadx",
                "args": ["-d", "{output_dir}", "{apk_path}"],
                "output_type": "source_code",
                "priority": 1
            },
            "apktool": {
                "name": "apktool", 
                "description": "Tool for reverse engineering Android APK files",
                "command": "apktool",
                "args": ["d", "{apk_path}", "-o", "{output_dir}", "-f"],
                "output_type": "resources_smali",
                "priority": 1
            },
            "strings": {
                "name": "strings",
                "description": "Extract strings from binary files",
                "command": "strings",
                "args": ["{apk_path}"],
                "output_type": "text_strings",
                "priority": 2
            },
            
            # Flutter-specific tools
            "reFlutter": {
                "name": "reFlutter",
                "description": "Flutter app patching and analysis tool",
                "command": "python3",
                "args": ["reFlutter.py", "{apk_path}"],
                "output_type": "patched_apk",
                "priority": 1
            },
            "blutter": {
                "name": "blutter",
                "description": "Flutter bytecode analysis tool",
                "command": "blutter",
                "args": ["{apk_path}", "{output_dir}"],
                "output_type": "dart_analysis",
                "priority": 1
            },
            
            # React Native tools
            "js-beautify": {
                "name": "js-beautify",
                "description": "JavaScript beautifier and formatter",
                "command": "js-beautify",
                "args": ["{bundle_path}"],
                "output_type": "formatted_js",
                "priority": 2
            },
            "hermes-dec": {
                "name": "hermes-dec",
                "description": "Hermes bytecode decompiler",
                "command": "hermes-dec",
                "args": ["{bundle_path}", "-o", "{output_dir}"],
                "output_type": "decompiled_js",
                "priority": 1
            },
            
            # Dynamic analysis tools
            "frida": {
                "name": "frida",
                "description": "Dynamic instrumentation framework",
                "command": "frida",
                "args": ["-U", "-f", "{package_name}"],
                "output_type": "runtime_analysis",
                "priority": 3
            }
        }
        
        return tool_definitions.get(tool_name)
    
    def _get_analysis_strategy(self, app_type: str) -> Dict[str, Any]:
        """Get analysis strategy for the app type."""
        strategies = {
            "Native Android": {
                "phases": [
                    {
                        "name": "Static Analysis",
                        "description": "Decompile and analyze source code",
                        "tools": ["jadx", "apktool"],
                        "focus": ["API endpoints", "hardcoded strings", "network configs"]
                    },
                    {
                        "name": "Resource Analysis", 
                        "description": "Analyze app resources and manifest",
                        "tools": ["apktool", "aapt"],
                        "focus": ["strings.xml", "network_security_config", "permissions"]
                    },
                    {
                        "name": "Security Analysis",
                        "description": "Look for security vulnerabilities",
                        "tools": ["strings", "grep"],
                        "focus": ["credentials", "keys", "certificates"]
                    }
                ],
                "priority_locations": [
                    "smali files for bytecode analysis",
                    "Java source for API calls",
                    "strings.xml for configuration",
                    "AndroidManifest.xml for permissions"
                ]
            },
            
            "Flutter": {
                "phases": [
                    {
                        "name": "Asset Analysis",
                        "description": "Analyze Flutter assets and configuration",
                        "tools": ["apktool"],
                        "focus": ["flutter_assets", "AssetManifest.json", "config files"]
                    },
                    {
                        "name": "Dart Analysis",
                        "description": "Analyze Dart bytecode and snapshots",
                        "tools": ["blutter", "reFlutter"],
                        "focus": ["VM snapshots", "widget trees", "business logic"]
                    },
                    {
                        "name": "Native Bridge Analysis",
                        "description": "Analyze platform channel implementations", 
                        "tools": ["jadx"],
                        "focus": ["platform channels", "native plugins"]
                    }
                ],
                "priority_locations": [
                    "flutter_assets/ for configurations",
                    "VM snapshots for business logic",
                    "lib/ directories for native code",
                    "AssetManifest.json for resource mapping"
                ]
            },
            
            "React Native": {
                "phases": [
                    {
                        "name": "Bundle Analysis",
                        "description": "Analyze JavaScript bundles",
                        "tools": ["js-beautify", "hermes-dec"],
                        "focus": ["API calls", "component structure", "state management"]
                    },
                    {
                        "name": "Bridge Analysis",
                        "description": "Analyze React Native bridge",
                        "tools": ["jadx"],
                        "focus": ["native modules", "bridge communication"]
                    },
                    {
                        "name": "Asset Analysis",
                        "description": "Analyze app assets and resources",
                        "tools": ["apktool"],
                        "focus": ["bundle files", "assets", "configurations"]
                    }
                ],
                "priority_locations": [
                    "assets/index.android.bundle for main code",
                    "Native modules for bridge implementations",
                    "lib/ directories for React Native runtime",
                    "Source maps if available"
                ]
            }
        }
        
        # Default strategy for unknown types
        default_strategy = {
            "phases": [
                {
                    "name": "Universal Analysis",
                    "description": "Generic analysis approach",
                    "tools": ["jadx", "apktool", "strings"],
                    "focus": ["any HTTP URLs", "configuration files", "string resources"]
                }
            ],
            "priority_locations": [
                "Any text-based files",
                "Configuration files",
                "Resource directories",
                "Binary string extraction"
            ]
        }
        
        return strategies.get(app_type, default_strategy)
    
    def _get_tool_commands(self, app_type: str) -> Dict[str, List[str]]:
        """Get specific tool command templates for the app type."""
        commands = {
            "Native Android": {
                "jadx_analysis": [
                    "jadx -d {jadx_output} {apk_path}",
                    "find {jadx_output} -name '*.java' -exec grep -l 'http' {} \\;"
                ],
                "apktool_analysis": [
                    "apktool d {apk_path} -o {apktool_output} -f",
                    "grep -r 'http' {apktool_output}/res/values/",
                    "grep -r 'api\\|endpoint' {apktool_output}/"
                ],
                "string_extraction": [
                    "strings {apk_path} | grep -E 'https?://'",
                    "strings {apktool_output}/resources.arsc | grep -E 'https?://'"
                ]
            },
            
            "Flutter": {
                "asset_analysis": [
                    "unzip {apk_path} 'flutter_assets/*'",
                    "find flutter_assets/ -name '*.json' -exec cat {} \\;",
                    "strings flutter_assets/* | grep -E 'https?://'"
                ],
                "blutter_analysis": [
                    "blutter {apk_path} {blutter_output}",
                    "grep -r 'http' {blutter_output}/"
                ]
            },
            
            "React Native": {
                "bundle_extraction": [
                    "unzip {apk_path} assets/index.android.bundle",
                    "js-beautify assets/index.android.bundle > readable.js",
                    "grep -E 'https?://' readable.js"
                ],
                "hermes_analysis": [
                    "hermes-dec assets/index.android.bundle -o {hermes_output}",
                    "grep -r 'fetch\\|axios' {hermes_output}/"
                ]
            }
        }
        
        return commands.get(app_type, commands["Native Android"])
    
    def _get_expected_artifacts(self, app_type: str) -> List[str]:
        """Get expected analysis artifacts for the app type."""
        artifacts = {
            "Native Android": [
                "Decompiled Java/Kotlin source code",
                "Android resources and layouts", 
                "Manifest with permissions and components",
                "String resources with potential URLs",
                "Network security configurations",
                "Obfuscated code patterns"
            ],
            
            "Flutter": [
                "Flutter assets and configurations",
                "Dart VM snapshots",
                "Widget composition trees",
                "Platform channel implementations",
                "Asset manifest mappings",
                "Plugin configurations"
            ],
            
            "React Native": [
                "JavaScript bundle files",
                "React component definitions",
                "API service definitions", 
                "Navigation structures",
                "State management patterns",
                "Native module interfaces"
            ],
            
            "Xamarin": [
                ".NET assemblies",
                "Mono runtime configurations",
                "Cross-platform abstractions",
                "Platform-specific implementations"
            ],
            
            "Cordova": [
                "HTML/JavaScript web content",
                "Cordova plugin configurations",
                "WebView bridge implementations", 
                "Plugin manifest files"
            ],
            
            "Unity": [
                "Unity asset bundles",
                "Game object hierarchies",
                "Script assemblies",
                "Resource asset mappings"
            ]
        }
        
        return artifacts.get(app_type, artifacts["Native Android"])


def select_tools_for_app(app_type: str, confidence: str = "Medium") -> Dict[str, Any]:
    """
    Convenience function to select tools for an app type.
    
    Args:
        app_type: The identified app type
        confidence: Confidence level of the identification
        
    Returns:
        Dict with tool selection and analysis strategy
    """
    selector = ToolSelector()
    return selector.select_tools(app_type, confidence)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python select_tools.py <app_type> [confidence]")
        print("App types: 'Native Android', 'Flutter', 'React Native', 'Xamarin', 'Cordova', 'Unity'")
        sys.exit(1)
    
    app_type = sys.argv[1]
    confidence = sys.argv[2] if len(sys.argv) > 2 else "Medium"
    
    result = select_tools_for_app(app_type, confidence)
    
    print(f"SELECTED TOOLS FOR: {result['app_type']} (Confidence: {result['confidence']})")
    print("\nPRIMARY TOOLS:")
    for tool in result['primary_tools']:
        if tool:
            print(f"- {tool['name']}: {tool['description']}")
    
    print("\nANALYSIS STRATEGY:")
    for phase in result['analysis_strategy']['phases']:
        print(f"- {phase['name']}: {phase['description']}")
        print(f"  Focus: {', '.join(phase['focus'])}")
    
    print(f"\nEXPECTED ARTIFACTS:")
    for artifact in result['expected_artifacts']:
        print(f"- {artifact}")
