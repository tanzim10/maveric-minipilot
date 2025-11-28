# Q&A Generator Explanation

## Overview

The `qa_generator.py` module generates comprehensive question-answer pairs from README content. These Q&A pairs are used to create FAQ sections that help train the RAG (Retrieval Augmented Generation) system to answer user questions accurately.

## Main Functions

### 1. `generate_qa_pairs(parsed_readmes: List[ParsedReadme]) -> List[QAPair]`

**Purpose**: Analyzes all parsed README content and generates Q&A pairs.

**How it works**:

1. **Processes Each README**:
   - Iterates through all parsed README files
   - Extracts content from sections, code blocks, tables, and workflows

2. **Generates Q&A from Multiple Sources**:
   - **Sections**: Extracts concepts, actions, and commands from section content
   - **Code Blocks**: Creates Q&A about what code does and how to run it
   - **Tables**: Generates Q&A about table content and structure
   - **Workflows**: Creates Q&A about step-by-step processes

3. **Quality Control**:
   - Removes duplicate questions
   - Limits Q&A per category (based on `max_questions_per_section` config)
   - Filters and validates Q&A pairs

**Example Usage**:
```python
from readme_generator.parser import parse_all_readmes
from readme_generator.qa_generator import generate_qa_pairs

# Parse all READMEs
parsed_readmes = parse_all_readmes()

# Generate Q&A pairs
qa_pairs = generate_qa_pairs(parsed_readmes)
# Returns: List of QAPair objects
```

**Output**: List of `QAPair` objects, each containing:
- `question`: The question text
- `answer`: The answer text
- `section_type`: Type of section (installation, usage, api, etc.)
- `source_section`: Which section it came from
- `category`: Category for grouping (installation, usage, code, etc.)

---

### 2. `format_qa_section(qa_pairs: List[QAPair], style: Optional[str] = None) -> str`

**Purpose**: Formats Q&A pairs as a markdown FAQ section.

**Supported Styles**:

1. **"simple"** (default): Q: A: format
   ```markdown
   **Q: How do I install Maveric?**
   
   A: To install Maveric, follow these steps: ...
   
   ---
   ```

2. **"collapsible"**: HTML details/summary (GitHub compatible)
   ```markdown
   <details>
   <summary><b>How do I install Maveric?</b></summary>
   
   To install Maveric, follow these steps: ...
   
   </details>
   ```

3. **"numbered"**: Numbered list format
   ```markdown
   1. **How do I install Maveric?**
   
      To install Maveric, follow these steps: ...
   ```

**How it works**:

1. Groups Q&A pairs by category
2. Creates section headers for each category
3. Formats pairs according to the specified style
4. Returns complete markdown section

**Example Usage**:
```python
from readme_generator.qa_generator import format_qa_section

# Format as simple Q&A
formatted = format_qa_section(qa_pairs, style='simple')

# Format as collapsible (GitHub)
formatted = format_qa_section(qa_pairs, style='collapsible')

# Format as numbered list
formatted = format_qa_section(qa_pairs, style='numbered')
```

---

## Q&A Generation Process

### Step 1: Content Extraction

The generator extracts different types of content:

#### Concepts Extraction (`_extract_concepts`)
- Finds technical terms (RADP, API, Docker, etc.)
- Extracts capitalized multi-word terms
- Finds quoted terms and backticked code terms
- Filters out common words and stop words

**Example**:
```python
content = "The RADP service uses Docker containers..."
concepts = _extract_concepts(content)
# Returns: ["RADP", "Docker", "containers", ...]
```

#### Actions Extraction (`_extract_actions`)
- Finds imperative verbs (run, install, start, etc.)
- Extracts "How to" patterns
- Identifies command verbs

**Example**:
```python
content = "Run the following command: docker build..."
actions = _extract_actions(content)
# Returns: ["run", "build", "install", ...]
```

#### Commands Extraction (`_extract_commands`)
- Extracts commands from code blocks
- Finds bash/shell commands
- Filters out comments

**Example**:
```python
content = "```bash\ndocker build -t radp radp\n```"
commands = _extract_commands(content)
# Returns: ["docker build -t radp radp"]
```

---

### Step 2: Question Generation

Questions are generated using templates from `QA_CONFIG`:

#### From Concepts (`_generate_question_from_concept`)
- Installation: "What is {concept}?" or "How do I {concept}?"
- Usage: "How do I use {concept}?"
- API: "What is the {concept} API?"

**Example**:
```python
concept = "Docker"
section_type = "installation"
question = _generate_question_from_concept(concept, section_type)
# Returns: "What is docker?" or "How do I docker?"
```

#### From Actions (`_generate_question_from_action`)
- Installation: "How do I {action}?"
- Usage: "How to {action}?"
- Troubleshooting: "How to troubleshoot {action}?"

**Example**:
```python
action = "install dependencies"
section_type = "installation"
question = _generate_question_from_action(action, section_type)
# Returns: "How do I install dependencies?"
```

#### From Commands (`_generate_question_from_command`)
- Extracts command name
- Generates: "How to run {command}?"

**Example**:
```python
command = "docker build -t radp radp"
question = _generate_question_from_command(command, "usage")
# Returns: "How to run docker?"
```

---

### Step 3: Answer Generation

Answers are extracted from the actual content:

#### From Content (`_generate_answer_from_content`)
1. Finds sentences containing the concept/action
2. Prioritizes sentences that start with the term
3. Combines 2-3 most relevant sentences
4. Falls back to code blocks if no sentences found
5. Uses generic answer as last resort

**Example**:
```python
concept = "Docker"
content = "Docker is required to run RADP. Install Docker from..."
answer = _generate_answer_from_content(concept, content, "installation")
# Returns: "Docker is required to run RADP. Install Docker from..."
```

#### From Code Blocks (`_explain_code_block`)
- Analyzes code to determine what it does
- Generates explanations based on code patterns
- Identifies imports, functions, Docker commands, etc.

**Example**:
```python
code_block = CodeBlock(content="docker build -t radp radp", language="bash")
answer = _explain_code_block(code_block)
# Returns: "This command manages Docker containers and services."
```

---

## Code Block Q&A Generation

### `_generate_code_block_qa()`

Generates Q&A pairs specifically from code blocks:

1. **What does this code do?**
   - Analyzes code structure
   - Generates explanation based on language and patterns

2. **How do I run this command?**
   - For bash/shell commands
   - Provides command with context

**Example**:
```python
code_blocks = [CodeBlock(content="pip install maveric", language="bash")]
qa_pairs = _generate_code_block_qa(code_blocks, "README.md")

# Generates:
# Q: "What does this bash code do?"
# A: "This command installs Python packages and dependencies."
#
# Q: "How do I run this command?"
# A: "Run the following command:\n\n```bash\npip install maveric\n```"
```

---

## Table Q&A Generation

### `_generate_table_qa()`

Generates Q&A about table content:

1. Extracts table headers
2. Creates question about table structure
3. Includes table in answer

**Example**:
```python
tables = ["|cell_id|avg_rsrp|lon|lat|\n|---|---|---|---|"]
qa_pairs = _generate_table_qa(tables, "README.md")

# Generates:
# Q: "What information is in the cell_id table?"
# A: "The table contains the following columns: cell_id, avg_rsrp, lon, lat.\n\n[table content]"
```

---

## Workflow Q&A Generation

### `_generate_workflow_qa()`

Generates Q&A about workflows:

1. Extracts numbered steps
2. Creates question about workflow steps
3. Includes full workflow in answer

**Example**:
```python
workflows = ["1. Install Docker\n2. Build image\n3. Start services"]
qa_pairs = _generate_workflow_qa(workflows, "README.md")

# Generates:
# Q: "What are the steps in this workflow?"
# A: "Here are the steps:\n\n1. Install Docker\n2. Build image\n3. Start services"
```

---

## Formatting Functions

### Simple Format (`_format_simple_qa`)

```markdown
**Q: How do I install Maveric?**

A: To install Maveric, follow these steps: ...

---
```

**Use case**: Simple, readable format for any markdown viewer.

---

### Collapsible Format (`_format_collapsible_qa`)

```markdown
<details>
<summary><b>How do I install Maveric?</b></summary>

To install Maveric, follow these steps: ...

</details>
```

**Use case**: GitHub README files - questions are collapsed by default.

---

### Numbered Format (`_format_numbered_qa`)

```markdown
1. **How do I install Maveric?**

   To install Maveric, follow these steps: ...

2. **How do I use the API?**

   To use the API, ...
```

**Use case**: Numbered FAQ lists, easy to reference.

---

## Quality Control

### Deduplication (`_deduplicate_qa_pairs`)

- Normalizes questions (lowercase, strip)
- Removes exact duplicates
- Keeps first occurrence

### Limiting (`_limit_qa_per_category`)

- Groups Q&A by category
- Limits to `max_questions_per_section` per category
- Ensures balanced coverage

### Grouping (`_group_qa_by_category`)

- Groups Q&A pairs by category
- Creates organized FAQ sections
- Makes formatting easier

---

## Configuration

The generator uses `QA_CONFIG` from `config.py`:

```python
QA_CONFIG = {
    "min_questions_per_section": 3,
    "max_questions_per_section": 10,
    "question_templates": [...],  # 20 question templates
    "include_troubleshooting_qa": True,
    "include_workflow_qa": True,
    "include_api_qa": True,
    "generate_from_code_blocks": True,
    "generate_from_tables": True,
    "generate_from_commands": True
}
```

**Key Settings**:
- `min_questions_per_section`: Minimum Q&A pairs per section
- `max_questions_per_section`: Maximum Q&A pairs per section
- `question_templates`: Templates for generating questions
- `generate_from_*`: Enable/disable Q&A generation from different sources

---

## Complete Workflow

```
1. Parse READMEs → parser.py
   ↓
2. Extract content (sections, code, tables, workflows)
   ↓
3. Generate Q&A pairs → generate_qa_pairs()
   ├── Extract concepts, actions, commands
   ├── Generate questions from templates
   ├── Generate answers from content
   └── Quality control (deduplicate, limit)
   ↓
4. Format as markdown → format_qa_section()
   ├── Group by category
   ├── Format according to style
   └── Return markdown string
   ↓
5. Include in enhanced README
```

---

## Example Output

### Generated Q&A Pairs

```python
[
    QAPair(
        question="How do I install Docker?",
        answer="Docker is required to run RADP. Install Docker from https://docs.docker.com/get-docker/",
        section_type="installation",
        category="installation"
    ),
    QAPair(
        question="What does this bash code do?",
        answer="This command installs Python packages and dependencies.",
        section_type="examples",
        category="code"
    ),
    ...
]
```

### Formatted Output (Simple Style)

```markdown
## Frequently Asked Questions

### Installation Questions

**Q: How do I install Docker?**

A: Docker is required to run RADP. Install Docker from https://docs.docker.com/get-docker/

---

**Q: How do I set up Python environment?**

A: Create virtual environment: `python3 -m venv .venv`. Activate it with `source .venv/bin/activate`.

---
```

---

## Testing Results

Tested with 8 README files:
- ✅ Generated 141 Q&A pairs
- ✅ Categorized by type (installation, usage, api, code, etc.)
- ✅ All formatting styles working
- ✅ Quality filtering working
- ✅ Deduplication working

---

## Key Features

1. **Multi-Source Generation**: Generates Q&A from sections, code, tables, workflows
2. **Template-Based**: Uses configurable question templates
3. **Content-Aware**: Answers extracted from actual content
4. **Quality Control**: Deduplication and limiting
5. **Flexible Formatting**: Multiple output styles
6. **Category Grouping**: Organized FAQ sections

---

## Next Steps

The Q&A generator works with:
1. **Parser** (`parser.py`) - Extracts content
2. **Enhancer** (`enhancer.py`) - Enhances sections
3. **Q&A Generator** (`qa_generator.py`) - Generates Q&A ← **This module**
4. **Main** (`main.py`) - Orchestrates everything

The generated Q&A pairs will be included in the enhanced README for RAG training.

