# Auto Queue Refactoring Summary - Plan 5 Implementation

## Overview

Successfully refactored `auto_queue.py` to implement Plan 5: **Simple Steps
dengan Markdown Prompts** approach.

## New Structure Created

### 📁 Folder Structure

```
prompts/
├── identification/
│   └── app_type_detection.md
├── tool_selection/
│   ├── kotlin_tools.md
│   ├── flutter_tools.md
│   └── react_native_tools.md
└── analysis/
    ├── kotlin_analysis.md
    ├── flutter_analysis.md
    ├── react_native_analysis.md
    └── generic_analysis.md

scripts/
├── auto_queue.py (refactored)
├── step_runner.py (new)
└── steps/
    ├── __init__.py
    ├── identify_app_type.py
    ├── select_tools.py
    └── analyze_app.py
```

### 🔄 New 3-Step Analysis Pipeline

#### Step 1: App Type Identification (`identify_app_type.py`)

- **Purpose**: Identifies technology stack (Native Android, Flutter, React
  Native, etc.)
- **Features**:
  - Filesystem analysis for framework signatures
  - Evidence collection with confidence scoring
  - Support for 6 app types: Native Android, Flutter, React Native, Xamarin,
    Cordova, Unity
  - Detailed reasoning for identification

#### Step 2: Tool Selection (`select_tools.py`)

- **Purpose**: Selects appropriate analysis tools based on app type
- **Features**:
  - Primary and fallback tool recommendations
  - App-type specific analysis strategies
  - Tool command templates
  - Expected artifacts mapping

#### Step 3: App Analysis (`analyze_app.py`)

- **Purpose**: Performs detailed analysis using Claude with targeted prompts
- **Features**:
  - Context-aware analysis (manifest, file structure, existing endpoints)
  - App-type specific prompt selection
  - Endpoint extraction and curl command generation
  - Security findings and auth flow analysis

### 📝 Markdown Prompts System

#### Identification Prompts

- `app_type_detection.md`: Comprehensive guide for identifying app technologies

#### Tool Selection Prompts

- `kotlin_tools.md`: Native Android analysis tools and strategies
- `flutter_tools.md`: Flutter-specific tools (reFlutter, blutter, etc.)
- `react_native_tools.md`: React Native bundle analysis tools

#### Analysis Prompts

- `kotlin_analysis.md`: Endpoint discovery in Native Android apps
- `flutter_analysis.md`: Flutter asset and Dart analysis strategies
- `react_native_analysis.md`: JavaScript bundle analysis techniques
- `generic_analysis.md`: Fallback analysis for unknown app types

## 🔧 Integration Changes

### Updated `auto_queue.py`

- **Enhanced pipeline**: Added step-based analysis after basic decompilation
- **Fallback system**: Legacy AI analysis if step-based fails
- **Better logging**: Detailed progress reporting for each step
- **Backwards compatible**: Still works with existing workflow

### New `step_runner.py`

- **Orchestration**: Coordinates execution of all 3 steps
- **Result consolidation**: Combines outputs from all steps
- **Error handling**: Graceful failure handling with detailed error reporting
- **Comprehensive output**: JSON results + human-readable summaries

## 🚀 Improved Workflow

### Before (Old Pipeline)

1. Decompile with apktool → `/decompiled`
2. Decompile with jadx → `/jadx_output`
3. Extract endpoints → `/curl.txt`
4. Generic AI analysis → `/ai_analysis.txt`

### After (New Pipeline)

1. Decompile with apktool → `/decompiled`
2. Decompile with jadx → `/jadx_output`
3. **STEP 1**: Identify app type → `/step1_identification.json`
4. **STEP 2**: Select tools → `/step2_tool_selection.json`
5. **STEP 3**: Specialized analysis → `/step3_analysis.json`
6. Extract endpoints → `/curl.txt` (enhanced)
7. Generate comprehensive report → `/pipeline_results.json` +
   `/analysis_summary.txt`

## 📊 Enhanced Output

### New Files Generated

- `step1_identification.json`: App type detection results
- `step2_tool_selection.json`: Selected tools and strategies
- `step3_analysis.json`: Detailed analysis results
- `pipeline_results.json`: Complete pipeline output
- `analysis_summary.txt`: Human-readable summary
- `curl.txt`: Enhanced with Claude-discovered endpoints

### Improved Analysis Quality

- **App-type awareness**: Different strategies for Flutter vs React Native vs
  Native Android
- **Targeted prompts**: Specialized analysis techniques per technology
- **Better endpoint discovery**: Technology-specific obfuscation handling
- **Comprehensive reporting**: Structured results with confidence levels

## 🎯 Key Benefits

1. **Modular**: Easy to add new app types or update prompts
2. **Maintainable**: Prompts in markdown files, easily editable
3. **Extensible**: Clear plugin points for new analysis steps
4. **Debuggable**: Step-by-step results for troubleshooting
5. **Fallback**: Graceful degradation if advanced analysis fails
6. **Team-friendly**: Non-developers can modify prompts

## 🔧 Usage

### Automatic (via auto_queue.py)

```bash
python3 scripts/auto_queue.py --once
python3 scripts/auto_queue.py --watch
```

### Manual Step Execution

```bash
# Run individual steps
python3 scripts/steps/identify_app_type.py /path/to/decompiled /path/to/jadx
python3 scripts/steps/select_tools.py "Native Android" "High"
python3 scripts/steps/analyze_app.py /path/to/workdir "Native Android" "High"

# Run complete pipeline
python3 scripts/step_runner.py /path/to/analysis/workdir
```

## ⚠️ Requirements

- All original requirements (apktool, jadx, claude CLI)
- Python 3.8+ with typing support
- ANTHROPIC_API_KEY environment variable for Claude analysis

## 🚧 Ready for Testing

The refactoring is complete and ready for testing. The system maintains backward
compatibility while providing significantly enhanced analysis capabilities
through the step-based approach.
