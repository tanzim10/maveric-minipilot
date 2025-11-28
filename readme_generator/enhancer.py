"""
Enhancer module for README sections.

This module provides functions to enhance parsed README sections by:
- Adding expanded examples and workflows
- Enhancing code blocks with comments and variations
- Adding step-by-step guides
- Expanding sections with detailed instructions
"""

import re
from typing import Dict, List, Optional
from readme_generator.parser import Section, CodeBlock
from readme_generator.config import (
    ENHANCEMENT_CONFIG,
    CODE_BLOCK_CONFIG,
    get_enhancement_config,
)


def enhance_section(section: Section, section_type: Optional[str] = None) -> str:
    """
    Enhance a section with examples, workflows, and expanded content.
    
    This is the main function that orchestrates all enhancements based on
    the section type and configuration settings.
    
    Args:
        section: The Section object to enhance
        section_type: Optional override for section type (defaults to section.section_type)
    
    Returns:
        Enhanced markdown content as a string
    """
    if section_type is None:
        section_type = section.section_type
    
    # Get enhancement configuration for this section type
    enhancement_config = get_enhancement_config(section_type)
    
    # Start with original content
    enhanced_content = section.content
    
    # Add section header
    header = f"{'#' * section.level} {section.title}\n\n"
    
    # Enhance based on section type
    if section_type == "installation":
        enhanced_content = _enhance_installation_section(section, enhancement_config, enhanced_content)
    elif section_type == "usage":
        enhanced_content = _enhance_usage_section(section, enhancement_config, enhanced_content)
    elif section_type == "api":
        enhanced_content = _enhance_api_section(section, enhancement_config, enhanced_content)
    elif section_type == "examples":
        enhanced_content = _enhance_examples_section(section, enhancement_config, enhanced_content)
    elif section_type == "workflow":
        enhanced_content = _enhance_workflow_section(section, enhancement_config, enhanced_content)
    elif section_type == "configuration":
        enhanced_content = _enhance_configuration_section(section, enhancement_config, enhanced_content)
    elif section_type == "troubleshooting":
        enhanced_content = _enhance_troubleshooting_section(section, enhancement_config, enhanced_content)
    else:
        # Generic enhancement for unknown sections
        enhanced_content = _enhance_generic_section(section, enhanced_content)
    
    # Enhance code blocks in the content
    if CODE_BLOCK_CONFIG.get("expand_minimal_blocks", True):
        enhanced_content = add_code_examples(enhanced_content, section.code_blocks)
    
    # Add workflow examples if applicable
    if section_type in ["usage", "workflow", "installation"]:
        workflow_examples = add_workflow_examples(section.title, section.content, section_type)
        if workflow_examples:
            enhanced_content += "\n\n" + workflow_examples
    
    return header + enhanced_content


def add_workflow_examples(
    section_title: str,
    section_content: str,
    section_type: str
) -> str:
    """
    Generate step-by-step workflow examples for a section.
    
    This function analyzes the section content and generates comprehensive
    step-by-step guides that walk users through processes.
    
    Args:
        section_title: Title of the section
        section_content: Content of the section
        section_type: Type of section (installation, usage, workflow, etc.)
    
    Returns:
        Markdown string with workflow examples, or empty string if none generated
    """
    workflows = []
    
    # Check if section already has numbered steps
    has_steps = bool(re.search(r"^\d+\.\s+", section_content, re.MULTILINE))
    
    if section_type == "installation":
        workflows.append(_generate_installation_workflow(section_content))
    elif section_type == "usage":
        workflows.append(_generate_usage_workflow(section_content))
    elif section_type == "workflow":
        workflows.append(_generate_generic_workflow(section_title, section_content))
    
    # If no workflows generated, try to extract from existing content
    if not workflows and not has_steps:
        workflows.append(_extract_and_enhance_workflow(section_content))
    
    return "\n\n".join(filter(None, workflows))


def add_code_examples(content: str, code_blocks: List[CodeBlock]) -> str:
    """
    Expand code blocks in content with comments, variations, and explanations.
    
    This function finds code blocks in the content and enhances them by:
    - Adding explanatory comments
    - Providing variations/alternatives
    - Adding error handling examples
    - Expanding minimal code blocks
    
    Args:
        content: Original markdown content
        code_blocks: List of CodeBlock objects found in the section
    
    Returns:
        Enhanced content with expanded code blocks
    """
    enhanced = content
    
    # Process each code block
    for code_block in code_blocks:
        if code_block.is_inline:
            # Skip inline code blocks (they're usually just variable names)
            continue
        
        # Find the code block in content
        code_pattern = re.escape(code_block.content[:50])  # Use first 50 chars as identifier
        pattern = rf"```{code_block.language or ''}\n.*?{code_pattern}.*?\n```"
        
        if re.search(pattern, enhanced, re.DOTALL):
            # Expand this code block
            expanded = _expand_code_block(code_block)
            
            # Replace the original with expanded version
            # Use a more specific pattern to avoid replacing wrong blocks
            original_block = f"```{code_block.language or ''}\n{code_block.content}\n```"
            if original_block in enhanced:
                enhanced = enhanced.replace(
                    original_block,
                    expanded,
                    1  # Replace only first occurrence
                )
    
    return enhanced


def _enhance_installation_section(
    section: Section,
    config: Dict[str, bool],
    content: str
) -> str:
    """Enhance installation section with detailed steps and platform-specific info."""
    enhanced = content
    
    if config.get("add_quick_start", False):
        quick_start = _generate_quick_start(section.content)
        if quick_start:
            enhanced = f"### Quick Start\n\n{quick_start}\n\n" + enhanced
    
    if config.get("add_detailed_steps", False):
        detailed_steps = _generate_detailed_steps(section.content)
        if detailed_steps:
            enhanced += "\n\n### Detailed Installation Steps\n\n" + detailed_steps
    
    if config.get("add_platform_specific", False):
        platform_info = _generate_platform_specific_info()
        if platform_info:
            enhanced += "\n\n### Platform-Specific Instructions\n\n" + platform_info
    
    if config.get("add_verification", False):
        verification = _generate_verification_steps(section.content)
        if verification:
            enhanced += "\n\n### Verify Installation\n\n" + verification
    
    if config.get("add_common_issues", False):
        common_issues = _generate_common_issues(section.content)
        if common_issues:
            enhanced += "\n\n### Common Issues\n\n" + common_issues
    
    return enhanced


def _enhance_usage_section(
    section: Section,
    config: Dict[str, bool],
    content: str
) -> str:
    """Enhance usage section with examples and use cases."""
    enhanced = content
    
    if config.get("add_basic_example", False):
        basic_example = _generate_basic_example(section.content)
        if basic_example:
            enhanced += "\n\n### Basic Example\n\n" + basic_example
    
    if config.get("add_advanced_example", False):
        advanced_example = _generate_advanced_example(section.content)
        if advanced_example:
            enhanced += "\n\n### Advanced Example\n\n" + advanced_example
    
    if config.get("add_use_cases", False):
        use_cases = _generate_use_cases(section.content)
        if use_cases:
            enhanced += "\n\n### Use Cases\n\n" + use_cases
    
    if config.get("add_best_practices", False):
        best_practices = _generate_best_practices(section.content)
        if best_practices:
            enhanced += "\n\n### Best Practices\n\n" + best_practices
    
    return enhanced


def _enhance_api_section(
    section: Section,
    config: Dict[str, bool],
    content: str
) -> str:
    """Enhance API section with request/response examples and error handling."""
    enhanced = content
    
    if config.get("add_request_examples", False):
        request_examples = _generate_request_examples(section.content)
        if request_examples:
            enhanced += "\n\n### Request Examples\n\n" + request_examples
    
    if config.get("add_response_examples", False):
        response_examples = _generate_response_examples(section.content)
        if response_examples:
            enhanced += "\n\n### Response Examples\n\n" + response_examples
    
    if config.get("add_error_handling", False):
        error_handling = _generate_error_handling(section.content)
        if error_handling:
            enhanced += "\n\n### Error Handling\n\n" + error_handling
    
    return enhanced


def _enhance_examples_section(
    section: Section,
    config: Dict[str, bool],
    content: str
) -> str:
    """Enhance examples section with expanded code blocks."""
    enhanced = content
    
    if config.get("add_comments", False):
        # Code blocks will be enhanced by add_code_examples
        pass
    
    if config.get("add_variations", False):
        variations = _generate_code_variations(section.code_blocks)
        if variations:
            enhanced += "\n\n### Code Variations\n\n" + variations
    
    if config.get("add_output_examples", False):
        output_examples = _generate_output_examples(section.content)
        if output_examples:
            enhanced += "\n\n### Expected Output\n\n" + output_examples
    
    return enhanced


def _enhance_workflow_section(
    section: Section,
    config: Dict[str, bool],
    content: str
) -> str:
    """Enhance workflow section with step-by-step guides."""
    enhanced = content
    
    if config.get("add_step_by_step", False):
        step_by_step = _generate_step_by_step_guide(section.content)
        if step_by_step:
            enhanced += "\n\n### Step-by-Step Guide\n\n" + step_by_step
    
    if config.get("add_edge_cases", False):
        edge_cases = _generate_edge_cases(section.content)
        if edge_cases:
            enhanced += "\n\n### Edge Cases and Considerations\n\n" + edge_cases
    
    return enhanced


def _enhance_configuration_section(
    section: Section,
    config: Dict[str, bool],
    content: str
) -> str:
    """Enhance configuration section with all options and defaults."""
    enhanced = content
    
    if config.get("add_all_options", False):
        all_options = _generate_all_options(section.content)
        if all_options:
            enhanced += "\n\n### All Configuration Options\n\n" + all_options
    
    if config.get("add_defaults", False):
        defaults = _generate_default_values(section.content)
        if defaults:
            enhanced += "\n\n### Default Values\n\n" + defaults
    
    return enhanced


def _enhance_troubleshooting_section(
    section: Section,
    config: Dict[str, bool],
    content: str
) -> str:
    """Enhance troubleshooting section with solutions and debugging steps."""
    enhanced = content
    
    if config.get("add_solutions", False):
        solutions = _generate_solutions(section.content)
        if solutions:
            enhanced += "\n\n### Solutions\n\n" + solutions
    
    if config.get("add_debugging_steps", False):
        debugging = _generate_debugging_steps(section.content)
        if debugging:
            enhanced += "\n\n### Debugging Steps\n\n" + debugging
    
    return enhanced


def _enhance_generic_section(section: Section, content: str) -> str:
    """Generic enhancement for unknown section types."""
    # Just enhance code blocks
    return content


# ============================================================================
# Code Block Enhancement Functions
# ============================================================================

def _expand_code_block(code_block: CodeBlock) -> str:
    """
    Expand a code block with comments and explanations.
    
    Args:
        code_block: CodeBlock object to expand
    
    Returns:
        Enhanced markdown code block string
    """
    content = code_block.content
    language = code_block.language or ""
    
    # Don't expand if already long or has comments
    if len(content) > 200 or "//" in content or "#" in content:
        return f"```{language}\n{content}\n```"
    
    # Add explanatory comments based on language
    if language in ["python", "py", "python3"]:
        enhanced = _add_python_comments(content)
    elif language in ["bash", "sh", "shell", "console"]:
        enhanced = _add_bash_comments(content)
    elif language in ["json"]:
        enhanced = _add_json_comments(content)
    else:
        enhanced = content
    
    return f"```{language}\n{enhanced}\n```"


def _add_python_comments(code: str) -> str:
    """Add explanatory comments to Python code."""
    lines = code.split('\n')
    enhanced_lines = []
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Skip empty lines
        if not stripped:
            enhanced_lines.append(line)
            continue
        
        # Add comment for import statements
        if stripped.startswith("import ") or stripped.startswith("from "):
            enhanced_lines.append(line)
            if i == 0 or lines[i-1].strip() == "":
                enhanced_lines.append("  # Import required modules")
        
        # Add comment for function definitions
        elif stripped.startswith("def ") or stripped.startswith("class "):
            enhanced_lines.append(line)
            enhanced_lines.append("    # Function/class implementation")
        
        # Add comment for common patterns
        elif "=" in stripped and not stripped.startswith("#"):
            if "client" in stripped.lower() or "api" in stripped.lower():
                enhanced_lines.append(line)
                enhanced_lines.append("  # Initialize client/API connection")
            else:
                enhanced_lines.append(line)
        else:
            enhanced_lines.append(line)
    
    return '\n'.join(enhanced_lines)


def _add_bash_comments(code: str) -> str:
    """Add explanatory comments to bash/shell code."""
    lines = code.split('\n')
    enhanced_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        if not stripped or stripped.startswith("#"):
            enhanced_lines.append(line)
            continue
        
        # Add comments for common commands
        if stripped.startswith("docker "):
            enhanced_lines.append(f"# {_explain_docker_command(stripped)}")
            enhanced_lines.append(line)
        elif stripped.startswith("pip ") or stripped.startswith("pip3 "):
            enhanced_lines.append(f"# Install Python package(s)")
            enhanced_lines.append(line)
        elif stripped.startswith("python ") or stripped.startswith("python3 "):
            enhanced_lines.append(f"# Run Python script")
            enhanced_lines.append(line)
        elif "export " in stripped or "set " in stripped:
            enhanced_lines.append(f"# Set environment variable")
            enhanced_lines.append(line)
        else:
            enhanced_lines.append(line)
    
    return '\n'.join(enhanced_lines)


def _add_json_comments(code: str) -> str:
    """Add explanatory comments to JSON (as markdown comments since JSON doesn't support comments)."""
    # JSON doesn't support comments, so we'll add a note before the block
    return code  # JSON comments would need special handling


def _explain_docker_command(command: str) -> str:
    """Explain what a docker command does."""
    if "build" in command:
        return "Build Docker image"
    elif "compose" in command or "docker-compose" in command:
        return "Start services using Docker Compose"
    elif "run" in command:
        return "Run a Docker container"
    elif "exec" in command:
        return "Execute command in running container"
    else:
        return "Docker command"


# ============================================================================
# Workflow Generation Functions
# ============================================================================

def _generate_installation_workflow(content: str) -> str:
    """Generate installation workflow from content."""
    steps = []
    
    # Extract existing steps
    step_pattern = re.compile(r"^\d+\.\s+(.+)$", re.MULTILINE)
    existing_steps = step_pattern.findall(content)
    
    if existing_steps:
        steps = existing_steps
    else:
        # Generate from content analysis
        if "docker" in content.lower():
            steps.append("Install Docker and Docker Compose")
            steps.append("Build Docker image: `docker build -t radp radp`")
            steps.append("Start services: `docker compose -f dc.yml -f dc-prod.yml up -d --build`")
        
        if "python" in content.lower() or "pip" in content.lower():
            steps.append("Install Python 3.8-3.10")
            steps.append("Create virtual environment: `python3 -m venv .venv`")
            steps.append("Activate virtual environment")
            steps.append("Install dependencies: `pip install -r requirements.txt`")
    
    if not steps:
        return ""
    
    workflow = "Follow these steps to complete installation:\n\n"
    for i, step in enumerate(steps, 1):
        workflow += f"{i}. {step}\n"
    
    return workflow


def _generate_usage_workflow(content: str) -> str:
    """Generate usage workflow from content."""
    # Extract commands and create workflow
    command_pattern = re.compile(r"```(?:bash|console|shell)?\n(.*?)\n```", re.DOTALL)
    commands = command_pattern.findall(content)
    
    if not commands:
        return ""
    
    workflow = "### Complete Workflow\n\n"
    workflow += "Here's a step-by-step workflow to get started:\n\n"
    
    for i, cmd in enumerate(commands[:5], 1):  # Limit to 5 commands
        cmd_clean = cmd.strip().split('\n')[0]  # First line of command
        workflow += f"{i}. **Run command:**\n   ```bash\n   {cmd_clean}\n   ```\n\n"
    
    return workflow


def _generate_generic_workflow(title: str, content: str) -> str:
    """Generate generic workflow from section content."""
    # Look for numbered lists
    step_pattern = re.compile(r"^\d+\.\s+(.+)$", re.MULTILINE)
    steps = step_pattern.findall(content)
    
    if steps:
        workflow = f"### {title} Workflow\n\n"
        for i, step in enumerate(steps, 1):
            workflow += f"{i}. {step}\n"
        return workflow
    
    return ""


def _extract_and_enhance_workflow(content: str) -> str:
    """Extract workflow from content and enhance it."""
    # Look for common workflow indicators
    if "step" in content.lower() or "workflow" in content.lower():
        # Try to extract steps
        lines = content.split('\n')
        steps = []
        in_list = False
        
        for line in lines:
            if re.match(r"^[-*]\s+", line) or re.match(r"^\d+\.\s+", line):
                steps.append(line.strip())
                in_list = True
            elif in_list and line.strip():
                steps[-1] += " " + line.strip()
            elif in_list and not line.strip():
                in_list = False
        
        if steps:
            workflow = "### Step-by-Step Process\n\n"
            for i, step in enumerate(steps[:10], 1):  # Limit to 10 steps
                # Remove list markers
                step_clean = re.sub(r"^[-*]\s+", "", step)
                step_clean = re.sub(r"^\d+\.\s+", "", step_clean)
                workflow += f"{i}. {step_clean}\n"
            return workflow
    
    return ""


# ============================================================================
# Content Generation Helper Functions
# ============================================================================

def _generate_quick_start(content: str) -> str:
    """Generate quick start section."""
    # Extract first command or key instruction
    command_pattern = re.compile(r"```(?:bash|console|shell)?\n(.*?)\n```", re.DOTALL)
    commands = command_pattern.findall(content)
    
    if commands:
        first_cmd = commands[0].strip().split('\n')[0]
        return f"```bash\n{first_cmd}\n```\n\nThis is the fastest way to get started."
    
    return ""


def _generate_detailed_steps(content: str) -> str:
    """Generate detailed installation steps."""
    return "1. **Prerequisites**: Ensure you have Python 3.8-3.10 and Docker installed\n"
    "2. **Environment Setup**: Create and activate virtual environment\n"
    "3. **Dependencies**: Install required packages\n"
    "4. **Configuration**: Set up environment variables\n"
    "5. **Verification**: Test the installation"


def _generate_platform_specific_info() -> str:
    """Generate platform-specific installation instructions."""
    return """### macOS/Linux
```bash
source .venv/bin/activate
export PYTHONPATH="$(pwd)":$PYTHONPATH
```

### Windows
```cmd
.venv\Scripts\activate
set PYTHONPATH=%CD%
```"""


def _generate_verification_steps(content: str) -> str:
    """Generate verification steps."""
    return """Run the following to verify your installation:

```bash
python3 -c "import radp; print('Installation successful')"
```

Or test with an example:

```bash
python3 apps/example/example_app.py
```"""


def _generate_common_issues(content: str) -> str:
    """Generate common issues section."""
    issues = []
    
    if "python" in content.lower():
        issues.append("**Issue**: `ModuleNotFoundError`\n- **Solution**: Set PYTHONPATH or install missing packages")
    
    if "docker" in content.lower():
        issues.append("**Issue**: Docker permission denied\n- **Solution**: Add user to docker group or use sudo")
    
    if "port" in content.lower():
        issues.append("**Issue**: Port already in use\n- **Solution**: Change port in configuration or stop conflicting service")
    
    if issues:
        return "\n\n".join(issues)
    return ""


def _generate_basic_example(content: str) -> str:
    """Generate basic usage example."""
    # Extract first code block
    code_pattern = re.compile(r"```(?:python|py)?\n(.*?)\n```", re.DOTALL)
    code_blocks = code_pattern.findall(content)
    
    if code_blocks:
        example = code_blocks[0].strip()
        return f"```python\n{example}\n```"
    
    return ""


def _generate_advanced_example(content: str) -> str:
    """Generate advanced usage example."""
    # Look for multiple code blocks and combine
    code_pattern = re.compile(r"```(?:python|py)?\n(.*?)\n```", re.DOTALL)
    code_blocks = code_pattern.findall(content)
    
    if len(code_blocks) >= 2:
        return f"```python\n# Advanced example combining multiple operations\n{code_blocks[0]}\n\n# Additional operations\n{code_blocks[1]}\n```"
    
    return ""


def _generate_use_cases(content: str) -> str:
    """Generate use cases."""
    return """- **Network Optimization**: Adjust cell configurations for better coverage
- **Energy Savings**: Optimize power consumption while maintaining QoS
- **Load Balancing**: Distribute traffic across cells efficiently
- **Simulation**: Test network configurations before deployment"""


def _generate_best_practices(content: str) -> str:
    """Generate best practices."""
    return """- Always use virtual environments for Python projects
- Test with small datasets before running full simulations
- Monitor resource usage during training
- Keep Docker images updated
- Use version control for configurations"""


def _generate_request_examples(content: str) -> str:
    """Generate API request examples."""
    return """```python
# Example API request
response = client.train(
    model_id="my_model",
    params={"maxiter": 100},
    ue_training_data="data.csv",
    topology="topology.csv"
)
```"""


def _generate_response_examples(content: str) -> str:
    """Generate API response examples."""
    return """```json
{
    "status": "success",
    "model_id": "my_model",
    "message": "Training started"
}
```"""


def _generate_error_handling(content: str) -> str:
    """Generate error handling examples."""
    return """```python
try:
    result = client.train(...)
except Exception as e:
    print(f"Error: {e}")
    # Handle error appropriately
```"""


def _generate_code_variations(code_blocks: List[CodeBlock]) -> str:
    """Generate code variations."""
    if not code_blocks:
        return ""
    
    variations = []
    for cb in code_blocks[:3]:  # Limit to 3 variations
        if not cb.is_inline:
            variations.append(f"### Variation\n\n```{cb.language or ''}\n{cb.content}\n```")
    
    return "\n\n".join(variations)


def _generate_output_examples(content: str) -> str:
    """Generate expected output examples."""
    return """```text
Expected output:
- Status: success
- Results: [dataframe with results]
- Logs: [execution logs]
```"""


def _generate_step_by_step_guide(content: str) -> str:
    """Generate step-by-step guide."""
    return _extract_and_enhance_workflow(content)


def _generate_edge_cases(content: str) -> str:
    """Generate edge cases section."""
    return """- **Large datasets**: May require more memory or batch processing
- **Network timeouts**: Increase timeout settings for long-running operations
- **Concurrent requests**: Use connection pooling for multiple simultaneous requests"""


def _generate_all_options(content: str) -> str:
    """Generate all configuration options."""
    return "See configuration file for all available options and their descriptions."


def _generate_default_values(content: str) -> str:
    """Generate default values."""
    return "Default values are used if not specified in configuration."


def _generate_solutions(content: str) -> str:
    """Generate solutions for common problems."""
    return _generate_common_issues(content)


def _generate_debugging_steps(content: str) -> str:
    """Generate debugging steps."""
    return """1. Check logs: `docker logs <container-name>`
2. Verify services: `docker ps`
3. Test connectivity: `curl http://localhost:8081/health`
4. Review error messages for specific issues"""

