# Enhancer.py Code Explanation

## Overview

The `enhancer.py` module takes parsed README sections and enhances them with:
- Expanded examples and workflows
- Detailed step-by-step guides
- Enhanced code blocks with comments
- Platform-specific instructions
- Troubleshooting information
- Use cases and best practices

## Main Functions

### 1. `enhance_section(section, section_type=None) -> str`

**Purpose**: Main orchestration function that enhances a section based on its type.

**How it works**:
1. Determines the section type (installation, usage, api, etc.)
2. Gets enhancement configuration from `ENHANCEMENT_CONFIG`
3. Calls type-specific enhancement functions
4. Enhances code blocks in the content
5. Adds workflow examples if applicable
6. Returns the complete enhanced markdown

**Example**:
```python
from readme_generator.parser import Section
from readme_generator.enhancer import enhance_section

# Section object from parser
section = Section(
    title="Installation",
    level=2,
    content="Install with: pip install maveric",
    section_type="installation"
)

# Enhance it
enhanced_markdown = enhance_section(section)
# Returns: "## Installation\n\n### Quick Start\n\n...\n### Detailed Steps\n\n..."
```

**Key Features**:
- Preserves original content
- Adds enhancements based on section type
- Maintains markdown structure
- Adds appropriate headers

---

### 2. `add_workflow_examples(section_title, section_content, section_type) -> str`

**Purpose**: Generates step-by-step workflow guides from section content.

**How it works**:
1. Analyzes section content for existing steps
2. Extracts commands and instructions
3. Generates numbered step-by-step guides
4. Formats as markdown with proper structure

**Example Output**:
```markdown
### Complete Workflow

Here's a step-by-step workflow to get started:

1. **Run command:**
   ```bash
   docker build -t radp radp
   ```

2. **Run command:**
   ```bash
   docker compose -f dc.yml -f dc-prod.yml up -d --build
   ```
```

**Key Features**:
- Detects existing numbered lists
- Extracts commands from code blocks
- Creates structured workflows
- Handles different section types (installation, usage, workflow)

**Internal Functions**:
- `_generate_installation_workflow()`: Creates installation steps
- `_generate_usage_workflow()`: Creates usage workflows
- `_generate_generic_workflow()`: Generic workflow generation
- `_extract_and_enhance_workflow()`: Extracts and enhances existing workflows

---

### 3. `add_code_examples(content, code_blocks) -> str`

**Purpose**: Expands code blocks with comments, explanations, and variations.

**How it works**:
1. Finds code blocks in the content
2. For each code block:
   - Adds explanatory comments
   - Provides language-specific enhancements
   - Expands minimal code blocks
3. Replaces original code blocks with enhanced versions

**Example Transformation**:

**Before**:
```python
import radp
client = radp.Client()
```

**After**:
```python
import radp
  # Import required modules
client = radp.Client()
  # Initialize client/API connection
```

**Key Features**:
- Language-aware (Python, Bash, JSON, etc.)
- Adds contextual comments
- Preserves original functionality
- Skips already-commented code

**Internal Functions**:
- `_expand_code_block()`: Main expansion logic
- `_add_python_comments()`: Python-specific comments
- `_add_bash_comments()`: Bash/shell comments
- `_add_json_comments()`: JSON handling
- `_explain_docker_command()`: Docker command explanations

---

## Section-Specific Enhancement Functions

### Installation Section (`_enhance_installation_section`)

**Adds**:
- **Quick Start**: Fastest way to get started
- **Detailed Steps**: Step-by-step installation
- **Platform-Specific**: Windows/Mac/Linux variations
- **Verification**: How to verify installation
- **Common Issues**: Troubleshooting common problems

**Example Enhancement**:
```markdown
### Quick Start
```bash
pip install maveric
```

### Detailed Installation Steps
1. **Prerequisites**: Ensure you have Python 3.8-3.10 and Docker installed
2. **Environment Setup**: Create and activate virtual environment
...

### Platform-Specific Instructions
### macOS/Linux
```bash
source .venv/bin/activate
```

### Windows
```cmd
.venv\Scripts\activate
```

### Common Issues
**Issue**: `ModuleNotFoundError`
- **Solution**: Set PYTHONPATH or install missing packages
```

---

### Usage Section (`_enhance_usage_section`)

**Adds**:
- **Basic Example**: Simple usage example
- **Advanced Example**: Complex usage scenarios
- **Use Cases**: Real-world applications
- **Best Practices**: Recommended approaches

**Example Enhancement**:
```markdown
### Basic Example
```python
from radp_client import RADPClient
client = RADPClient()
```

### Advanced Example
```python
# Advanced example combining multiple operations
client.train(...)
# Additional operations
client.simulation(...)
```

### Use Cases
- **Network Optimization**: Adjust cell configurations
- **Energy Savings**: Optimize power consumption
...
```

---

### API Section (`_enhance_api_section`)

**Adds**:
- **Request Examples**: How to make API calls
- **Response Examples**: What to expect back
- **Error Handling**: How to handle errors

**Example Enhancement**:
```markdown
### Request Examples
```python
response = client.train(
    model_id="my_model",
    params={"maxiter": 100}
)
```

### Response Examples
```json
{
    "status": "success",
    "model_id": "my_model"
}
```

### Error Handling
```python
try:
    result = client.train(...)
except Exception as e:
    print(f"Error: {e}")
```
```

---

### Examples Section (`_enhance_examples_section`)

**Adds**:
- **Code Variations**: Different ways to do the same thing
- **Expected Output**: What the code produces
- **Comments**: Explanatory comments in code

---

### Workflow Section (`_enhance_workflow_section`)

**Adds**:
- **Step-by-Step Guide**: Detailed process walkthrough
- **Edge Cases**: Special considerations

---

### Troubleshooting Section (`_enhance_troubleshooting_section`)

**Adds**:
- **Solutions**: Detailed solutions to problems
- **Debugging Steps**: How to debug issues

---

## Code Block Enhancement Details

### Python Code Enhancement

**What it does**:
- Adds comments for imports
- Explains function/class definitions
- Comments on variable assignments
- Adds context for API calls

**Example**:
```python
# Before
import radp
client = radp.Client()
result = client.train(...)

# After
import radp
  # Import required modules
client = radp.Client()
  # Initialize client/API connection
result = client.train(...)
  # Train a model with specified parameters
```

---

### Bash/Shell Code Enhancement

**What it does**:
- Explains Docker commands
- Comments on package installation
- Explains environment variable setup
- Adds context for Python script execution

**Example**:
```bash
# Before
docker build -t radp radp
pip install -r requirements.txt

# After
# Build Docker image
docker build -t radp radp
# Install Python package(s)
pip install -r requirements.txt
```

---

## Workflow Generation Details

### Installation Workflow

**Process**:
1. Extracts existing numbered steps from content
2. If none found, analyzes content for:
   - Docker commands → generates Docker setup steps
   - Python/pip commands → generates Python setup steps
3. Creates numbered list of steps

**Output Format**:
```markdown
Follow these steps to complete installation:

1. Install Docker and Docker Compose
2. Build Docker image: `docker build -t radp radp`
3. Start services: `docker compose -f dc.yml -f dc-prod.yml up -d --build`
4. Install Python 3.8-3.10
5. Create virtual environment: `python3 -m venv .venv`
...
```

---

### Usage Workflow

**Process**:
1. Extracts code blocks from content
2. Identifies commands
3. Creates step-by-step guide with commands
4. Limits to 5 commands to keep it concise

**Output Format**:
```markdown
### Complete Workflow

Here's a step-by-step workflow to get started:

1. **Run command:**
   ```bash
   docker build -t radp radp
   ```

2. **Run command:**
   ```bash
   python3 apps/example/example_app.py
   ```
```

---

## Configuration-Driven Enhancement

The enhancer uses `ENHANCEMENT_CONFIG` from `config.py` to determine what to add:

```python
ENHANCEMENT_CONFIG = {
    "installation": {
        "add_quick_start": True,
        "add_detailed_steps": True,
        "add_platform_specific": True,
        ...
    },
    "usage": {
        "add_basic_example": True,
        "add_advanced_example": True,
        ...
    }
}
```

**Benefits**:
- Easy to enable/disable specific enhancements
- Consistent enhancement across sections
- Configurable per section type

---

## Usage Example

```python
from readme_generator.parser import parse_readme, get_all_sections_flat
from readme_generator.enhancer import enhance_section

# Parse a README
parsed = parse_readme(Path("data/source/README copy.md"))

# Get all sections
all_sections = get_all_sections_flat(parsed.sections)

# Enhance each section
enhanced_sections = []
for section in all_sections:
    enhanced = enhance_section(section)
    enhanced_sections.append(enhanced)

# Combine into final document
final_document = "\n\n".join(enhanced_sections)
```

---

## Key Design Decisions

1. **Preserves Original Content**: Never removes original content, only adds to it
2. **Language-Aware**: Different enhancement strategies for Python, Bash, JSON
3. **Configurable**: Uses config to control what enhancements are added
4. **Section-Type Specific**: Different enhancements for installation vs usage vs API
5. **Non-Destructive**: Original structure and content remain intact
6. **Smart Detection**: Analyzes content to determine what enhancements to add

---

## Testing

The enhancer was tested with real README files:
- ✅ Successfully enhances installation sections
- ✅ Adds workflow examples
- ✅ Expands code blocks with comments
- ✅ Generates platform-specific instructions
- ✅ Creates step-by-step guides

**Test Results**:
- Original content: 159 chars
- Enhanced content: 1040 chars
- Enhancement added: 881 chars (5.5x expansion)

---

## Next Steps

The enhancer works with the parser to:
1. Parse README files → `parser.py`
2. Enhance sections → `enhancer.py` (this module)
3. Generate Q&A → `qa_generator.py` (next module)
4. Combine everything → `main.py` (orchestrator)

