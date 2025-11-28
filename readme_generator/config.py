"""
Configuration settings for the README Generator module.

This module defines all configuration constants and settings used by
the readme_generator to parse, enhance, and generate README files.
"""

import os
from pathlib import Path
from typing import Dict, List

# Base directory paths
# Get the project root (parent of readme_generator directory)
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SOURCE_README_DIR = DATA_DIR / "source"
OUTPUT_FILE = DATA_DIR / "enhanced_readme.md"

# Ensure directories exist
SOURCE_README_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# File patterns to look for when scanning for README files
# Handles various naming conventions: spaces, dashes, underscores, "copy" suffix, typos
README_PATTERNS = [
    "README.md",
    "README*.md",
    "Readme*.md",
    "readme*.md",
    "README-*.md",           # README-DEV.md, README-MRO.md, etc.
    "Readme_*.md",           # Readme_Load_Balancing.md, etc.
    "DEVELOPER_GUIDE.md",
    "*_GUIDE.md",
    "*GUIDE*.md",            # DEVELOPER_GUIDE.md variations
    "*copy*.md",             # Files with "copy" in name (case insensitive)
    "*Copy*.md",
    "*COPY*.md"
]

# Case-insensitive file matching patterns (for glob matching)
README_FILE_EXTENSIONS = [".md", ".MD", ".Md", ".mD"]

# Common file name variations to handle
README_NAME_VARIATIONS = [
    "readme", "README", "Readme",
    "developer_guide", "DEVELOPER_GUIDE", "Developer_Guide",
    "guide", "GUIDE", "Guide"
]

# Markdown section headers to identify and enhance
# Handles numbered sections, question marks, all caps, variations, and deep nesting
SECTION_HEADERS = {
    "overview": [
        "## Overview", "### Overview", "#### Overview",
        "## 1. Overview", "## 1 Overview", "# Overview",
        "## Introduction", "### Introduction"
    ],
    "installation": [
        "## Installation", "### Installation", "#### Installation",
        "## Setup", "### Setup", "#### Setup",
        "## 2. Installation", "## Installing", "## Install",
        "## Environment Setup", "### Environment Setup",
        "## Prerequisites", "### Prerequisites", "#### Prerequisites",
        "## System Requirements", "### System Requirements",
        "## Quick Start", "### Quick Start"
    ],
    "usage": [
        "## Usage", "### Usage", "#### Usage",
        "## Getting Started", "### Getting Started",
        "## How to Use", "### How to Use",
        "## Application Workflow & Usage", "## Application Workflow",
        "## Execution Pipeline", "### Execution Pipeline",
        "## Running", "### Running"
    ],
    "api": [
        "## API", "### API", "#### API",
        "## API Reference", "### API Reference",
        "## Endpoints", "### Endpoints",
        "## Train API", "## Simulation API",
        "## Describe Model API", "## Describe Simulation API",
        "## Consume Simulation Output API"
    ],
    "examples": [
        "## Examples", "### Examples", "#### Examples",
        "## Example", "### Example",
        "## Code Examples", "### Code Examples",
        "## Sample", "### Sample"
    ],
    "workflow": [
        "## Workflow", "### Workflow", "#### Workflow",
        "## Workflows", "### Workflows",
        "## Process", "### Process",
        "## Development Workflow", "### Development Workflow",
        "## Pipeline", "### Pipeline"
    ],
    "configuration": [
        "## Configuration", "### Configuration", "#### Configuration",
        "## Config", "### Config",
        "## Settings", "### Settings",
        "## Configure", "### Configure"
    ],
    "troubleshooting": [
        "## Troubleshooting", "### Troubleshooting", "#### Troubleshooting",
        "## FAQ", "### FAQ",
        "## Common Issues", "### Common Issues", "#### Common Issues",
        "## Something wrong?", "## Something wrong",
        "## Problems", "### Problems",
        "## Issues", "### Issues",
        "## Getting Help", "### Getting Help"
    ],
    "prerequisites": [
        "## Prerequisites", "### Prerequisites", "#### Prerequisites",
        "## Requirements", "### Requirements",
        "## System Requirements", "### System Requirements",
        "## Optional Requirements", "### Optional Requirements"
    ],
    "structure": [
        "## Directory Structure", "### Directory Structure",
        "## Project Structure", "### Project Structure",
        "## Structure", "### Structure",
        "## File Structure", "### File Structure"
    ],
    "features": [
        "## Key Features", "### Key Features",
        "## Features", "### Features",
        "## 2. Key Features", "## Capabilities"
    ],
    "architecture": [
        "## System Architecture", "### System Architecture",
        "## Architecture", "### Architecture",
        "## Design", "### Design"
    ],
    "module_breakdown": [
        "## Detailed Module Breakdown", "### Detailed Module Breakdown",
        "## Module Breakdown", "### Module Breakdown",
        "## Modules", "### Modules"
    ],
    "license": [
        "## LICENSE", "## License", "### License",
        "## Licensing", "### Licensing"
    ],
    "table_of_contents": [
        "## Table of Contents", "### Table of Contents",
        "## Contents", "### Contents",
        "## TOC", "### TOC"
    ]
}

# Header level patterns (supports # through ######)
HEADER_PATTERNS = {
    "h1": r"^#\s+.+",           # # Header
    "h2": r"^##\s+.+",          # ## Header
    "h3": r"^###\s+.+",         # ### Header
    "h4": r"^####\s+.+",        # #### Header
    "h5": r"^#####\s+.+",       # ##### Header
    "h6": r"^######\s+.+",       # ###### Header
    "numbered_h2": r"^##\s+\d+\.\s+.+",  # ## 1. Header
    "numbered_h3": r"^###\s+\d+\.\s+.+", # ### 1. Header
}

# Section detection regex patterns (more flexible matching)
SECTION_DETECTION_PATTERNS = {
    "installation": [
        r"(?i)^#{1,6}\s+(installation|setup|install|installing|prerequisites|system\s+requirements)",
        r"(?i)^#{1,6}\s+\d+\.\s*(installation|setup|install)"
    ],
    "usage": [
        r"(?i)^#{1,6}\s+(usage|getting\s+started|how\s+to\s+use|running|execution)",
        r"(?i)^#{1,6}\s+\d+\.\s*(usage|getting\s+started)"
    ],
    "api": [
        r"(?i)^#{1,6}\s+(api|endpoints?|train\s+api|simulation\s+api)",
    ],
    "troubleshooting": [
        r"(?i)^#{1,6}\s+(troubleshooting|faq|common\s+issues?|problems?|something\s+wrong)",
    ]
}

# Enhancement configuration
# Controls what types of enhancements to add to each section
ENHANCEMENT_CONFIG: Dict[str, Dict[str, bool]] = {
    "overview": {
        "add_key_points": True,
        "add_use_cases": True,
        "add_benefits": True
    },
    "installation": {
        "add_quick_start": True,
        "add_detailed_steps": True,
        "add_prerequisites": True,
        "add_verification": True,
        "add_common_issues": True,
        "add_platform_specific": True,  # Windows/Mac/Linux variations
        "add_docker_setup": True,
        "add_gpu_setup": True
    },
    "usage": {
        "add_basic_example": True,
        "add_advanced_example": True,
        "add_use_cases": True,
        "add_best_practices": True,
        "add_command_line_examples": True,
        "add_full_workflow_example": True
    },
    "api": {
        "expand_endpoints": True,
        "add_request_examples": True,
        "add_response_examples": True,
        "add_error_handling": True,
        "add_parameter_descriptions": True,
        "add_code_examples": True
    },
    "examples": {
        "expand_code_blocks": True,
        "add_comments": True,
        "add_variations": True,
        "add_output_examples": True,
        "add_explanation": True
    },
    "workflow": {
        "add_step_by_step": True,
        "add_diagrams_description": True,
        "add_edge_cases": True,
        "add_sequential_steps": True,
        "add_parallel_options": True
    },
    "configuration": {
        "add_all_options": True,
        "add_defaults": True,
        "add_environment_variables": True,
        "add_json_examples": True,
        "add_validation_rules": True
    },
    "troubleshooting": {
        "expand_common_issues": True,
        "add_solutions": True,
        "add_prevention_tips": True,
        "add_error_messages": True,
        "add_debugging_steps": True
    },
    "prerequisites": {
        "expand_requirements": True,
        "add_version_specific": True,
        "add_optional_dependencies": True
    },
    "structure": {
        "add_file_descriptions": True,
        "add_directory_explanations": True
    },
    "features": {
        "expand_feature_descriptions": True,
        "add_feature_examples": True
    },
    "architecture": {
        "add_component_descriptions": True,
        "add_flow_descriptions": True
    },
    "module_breakdown": {
        "expand_module_details": True,
        "add_module_examples": True
    }
}

# Code block detection and handling
CODE_BLOCK_CONFIG = {
    "languages": [
        "bash", "sh", "shell", "console", "python", "py", "python3",
        "json", "yaml", "yml", "text", "markdown", "md",
        "javascript", "js", "typescript", "ts", "java", "go", "rust"
    ],
    "inline_code_pattern": r"`[^`]+`",  # Matches `code`
    "code_block_pattern": r"```[\s\S]*?```",  # Matches ```code```
    "fenced_code_block_pattern": r"^```[\w]*\n[\s\S]*?^```",  # Multiline
    "detect_language": True,  # Try to detect language from code content
    "preserve_language_tags": True,
    "expand_minimal_blocks": True,  # Expand very short code blocks
    "min_code_block_length": 10  # Minimum chars to consider it a code block
}

# Table detection and handling
TABLE_CONFIG = {
    "detect_tables": True,
    "preserve_table_formatting": True,
    "expand_table_descriptions": True,
    "add_table_examples": True,
    "table_pattern": r"^\|.+\|",  # Matches markdown table rows
    "table_separator_pattern": r"^\|[\s\-:]+\|"  # Matches table separator
}

# Link detection and handling
LINK_CONFIG = {
    "detect_markdown_links": True,  # [text](url)
    "detect_anchor_links": True,     # [text](#anchor)
    "detect_external_links": True,   # http://, https://
    "detect_file_links": True,       # Links to other files
    "preserve_links": True,
    "validate_links": False,  # Don't validate (would require file system access)
    "link_pattern": r"\[([^\]]+)\]\(([^\)]+)\)",
    "anchor_pattern": r"\[([^\]]+)\]\(#([^\)]+)\)"
}

# Special content detection
SPECIAL_CONTENT_CONFIG = {
    "detect_mermaid_diagrams": True,
    "detect_version_info": True,      # **Version:** 1.0
    "detect_dates": True,             # **Date:** June 20, 2025
    "detect_horizontal_rules": True,  # ---
    "detect_images": True,          # ![alt](url)
    "preserve_special_content": True,
    "mermaid_pattern": r"```mermaid[\s\S]*?```",
    "version_pattern": r"(?i)\*\*version\*\*:\s*[\d.]+",
    "date_pattern": r"(?i)\*\*date\*\*:\s*[\w\s,]+"
}

# Deep nesting support
NESTING_CONFIG = {
    "max_nesting_depth": 6,  # Support up to ###### headers
    "preserve_nesting": True,
    "normalize_excessive_nesting": False,  # Don't auto-normalize, preserve structure
    "detect_nested_lists": True,
    "detect_nested_code_blocks": True,
    "detect_nested_tables": True
}

# Q&A Generation settings
QA_CONFIG = {
    "min_questions_per_section": 3,
    "max_questions_per_section": 10,
    "question_templates": [
        "How do I {action}?",
        "What is {concept}?",
        "Why does {issue} happen?",
        "Can I {capability}?",
        "What happens when {scenario}?",
        "How to troubleshoot {problem}?",
        "What are the requirements for {feature}?",
        "How to configure {setting}?",
        "How does {feature} work?",
        "What is the purpose of {component}?",
        "How to set up {component}?",
        "What are the steps to {action}?",
        "How to run {command}?",
        "What does {parameter} do?",
        "How to fix {error}?",
        "What is the difference between {option1} and {option2}?",
        "How to use {tool}?",
        "What are the prerequisites for {task}?",
        "How to test {component}?",
        "What should I do if {situation}?"
    ],
    "include_troubleshooting_qa": True,
    "include_workflow_qa": True,
    "include_api_qa": True,
    "include_installation_qa": True,
    "include_configuration_qa": True,
    "include_examples_qa": True,
    "generate_from_code_blocks": True,  # Generate Q&A from code examples
    "generate_from_tables": True,        # Generate Q&A from table content
    "generate_from_commands": True       # Generate Q&A from command examples
}

# Output formatting settings
OUTPUT_CONFIG = {
    "include_table_of_contents": True,
    "include_module_separators": True,
    "module_separator_style": "horizontal_rule",  # Options: "horizontal_rule", "header", "both"
    "qa_section_style": "collapsible",  # Options: "collapsible", "simple", "numbered"
    "code_block_language": "auto",  # Auto-detect or specify language
    "max_line_length": 100
}

# Logging configuration
LOG_CONFIG = {
    "log_level": "INFO",  # DEBUG, INFO, WARNING, ERROR
    "log_file": None,  # Set to a path if you want file logging
    "verbose": False
}

# Processing options
PROCESSING_CONFIG = {
    "merge_duplicate_sections": True,
    "preserve_original_structure": True,
    "sort_sections": False,  # Keep original order if False
    "remove_empty_sections": True,
    "normalize_headers": False,  # Preserve original header levels (don't auto-normalize)
    "handle_numbered_sections": True,  # Handle "## 1. Section" format
    "preserve_special_characters": True,  # Preserve ?, !, etc. in headers
    "handle_case_variations": True,  # Handle "LICENSE" vs "License"
    "preserve_whitespace": True,  # Preserve intentional whitespace
    "handle_typos": False,  # Don't auto-correct (preserve original)
    "strip_trailing_whitespace": True,  # Clean up trailing spaces
    "normalize_line_endings": True,  # Convert \r\n to \n
    "preserve_blank_lines": True,  # Keep intentional blank lines
    "max_section_depth": 6,  # Maximum header depth to process
    "skip_very_deep_sections": False  # Don't skip, process all
}

# Edge case handling
EDGE_CASE_CONFIG = {
    "handle_files_with_spaces": True,  # "README copy.md"
    "handle_files_with_dashes": True,  # "README-DEV.md"
    "handle_files_with_underscores": True,  # "Readme_Load_Balancing.md"
    "handle_files_with_copy": True,  # "README copy.md", "README-DEV copy.md"
    "handle_typos_in_filenames": True,  # "Readme_Engery_Savings.md" (Energy typo)
    "handle_case_variations": True,  # "README.md" vs "readme.md"
    "handle_missing_extensions": False,  # Assume .md if missing
    "handle_empty_files": True,  # Skip or handle empty READMEs
    "handle_very_large_files": True,  # Files > 1MB
    "max_file_size_mb": 10,  # Maximum file size to process
    "handle_binary_content": False,  # Skip if binary detected
    "handle_encoding_issues": True,  # Handle UTF-8, Latin-1, etc.
    "preferred_encoding": "utf-8",
    "fallback_encodings": ["latin-1", "cp1252", "iso-8859-1"]
}

# Environment variable overrides
# Allow configuration to be overridden via environment variables
def get_config_from_env() -> Dict:
    """Get configuration overrides from environment variables."""
    env_config = {}
    
    if os.getenv("README_SOURCE_DIR"):
        env_config["SOURCE_README_DIR"] = Path(os.getenv("README_SOURCE_DIR"))
    
    if os.getenv("README_OUTPUT_FILE"):
        env_config["OUTPUT_FILE"] = Path(os.getenv("README_OUTPUT_FILE"))
    
    if os.getenv("README_LOG_LEVEL"):
        env_config["LOG_LEVEL"] = os.getenv("README_LOG_LEVEL")
    
    return env_config

# Apply environment overrides
_env_overrides = get_config_from_env()
if "SOURCE_README_DIR" in _env_overrides:
    SOURCE_README_DIR = _env_overrides["SOURCE_README_DIR"]
if "OUTPUT_FILE" in _env_overrides:
    OUTPUT_FILE = _env_overrides["OUTPUT_FILE"]
if "LOG_LEVEL" in _env_overrides:
    LOG_CONFIG["log_level"] = _env_overrides["LOG_LEVEL"]


def get_enhancement_config(section_type: str) -> Dict[str, bool]:
    """
    Get enhancement configuration for a specific section type.
    
    Args:
        section_type: The type of section (e.g., 'installation', 'usage')
    
    Returns:
        Dictionary of enhancement flags for that section type
    """
    return ENHANCEMENT_CONFIG.get(section_type, {})


def validate_config() -> List[str]:
    """
    Validate configuration settings and return any errors.
    
    Returns:
        List of error messages (empty if no errors)
    """
    errors = []
    
    # Check if source directory exists
    if not SOURCE_README_DIR.exists():
        errors.append(f"Source README directory does not exist: {SOURCE_README_DIR}")
    
    # Check if output directory is writable
    if not OUTPUT_FILE.parent.exists():
        try:
            OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            errors.append(f"Cannot create output directory: {e}")
    
    # Validate enhancement config
    for section_type, enhancements in ENHANCEMENT_CONFIG.items():
        if not isinstance(enhancements, dict):
            errors.append(f"Invalid enhancement config for {section_type}: must be a dict")
    
    # Validate regex patterns compile correctly
    import re
    for pattern_name, patterns in SECTION_DETECTION_PATTERNS.items():
        for pattern in patterns:
            try:
                re.compile(pattern)
            except re.error as e:
                errors.append(f"Invalid regex pattern in {pattern_name}: {pattern} - {e}")
    
    # Validate header patterns
    for pattern_name, pattern in HEADER_PATTERNS.items():
        try:
            re.compile(pattern)
        except re.error as e:
            errors.append(f"Invalid header pattern {pattern_name}: {pattern} - {e}")
    
    # Validate code block patterns
    for pattern_name, pattern in CODE_BLOCK_CONFIG.items():
        if "pattern" in pattern_name:
            try:
                re.compile(pattern)
            except (re.error, TypeError):
                pass  # Some patterns might not be strings
    
    # Validate edge case config
    if EDGE_CASE_CONFIG.get("max_file_size_mb", 0) <= 0:
        errors.append("max_file_size_mb must be greater than 0")
    
    return errors


def get_section_type_from_header(header_text: str) -> str:
    """
    Determine section type from header text using flexible matching.
    
    Handles numbered sections, case variations, special characters, etc.
    
    Args:
        header_text: The header text (e.g., "## Installation", "## 1. Overview")
    
    Returns:
        Section type string (e.g., "installation", "overview") or "unknown"
    """
    import re
    
    # Normalize header text (remove #, numbers, whitespace)
    normalized = re.sub(r"^#+\s*", "", header_text)  # Remove leading #
    normalized = re.sub(r"^\d+\.\s*", "", normalized)  # Remove leading "1. "
    normalized = normalized.strip().lower()
    
    # Remove special characters for matching
    normalized_clean = re.sub(r"[?!.,:;]", "", normalized)
    
    # Check each section type
    for section_type, headers in SECTION_HEADERS.items():
        for header_pattern in headers:
            # Normalize pattern header
            pattern_normalized = re.sub(r"^#+\s*", "", header_pattern)
            pattern_normalized = re.sub(r"^\d+\.\s*", "", pattern_normalized)
            pattern_normalized = pattern_normalized.strip().lower()
            pattern_clean = re.sub(r"[?!.,:;]", "", pattern_normalized)
            
            # Exact match or contains match
            if normalized_clean == pattern_clean or normalized_clean.startswith(pattern_clean):
                return section_type
    
    # Try regex patterns
    for section_type, patterns in SECTION_DETECTION_PATTERNS.items():
        for pattern in patterns:
            if re.match(pattern, header_text, re.IGNORECASE):
                return section_type
    
    return "unknown"


def should_process_file(file_path: Path) -> bool:
    """
    Determine if a file should be processed based on edge case config.
    
    Args:
        file_path: Path to the file
    
    Returns:
        True if file should be processed, False otherwise
    """
    if not file_path.exists():
        return False
    
    # Check file extension
    if file_path.suffix.lower() not in [ext.lower() for ext in README_FILE_EXTENSIONS]:
        return False
    
    # Check file size
    max_size_bytes = EDGE_CASE_CONFIG.get("max_file_size_mb", 10) * 1024 * 1024
    if file_path.stat().st_size > max_size_bytes:
        if not EDGE_CASE_CONFIG.get("handle_very_large_files", True):
            return False
    
    # Check if empty
    if file_path.stat().st_size == 0:
        return EDGE_CASE_CONFIG.get("handle_empty_files", True)
    
    return True

