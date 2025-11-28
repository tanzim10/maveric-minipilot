"""
Q&A Generator module for README files.

This module generates question-answer pairs from README content to create
comprehensive FAQ sections for training the RAG system.
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from readme_generator.parser import Section, ParsedReadme, CodeBlock
from readme_generator.config import (
    QA_CONFIG,
    OUTPUT_CONFIG,
)


@dataclass
class QAPair:
    """Represents a question-answer pair."""
    question: str
    answer: str
    section_type: str = "unknown"
    source_section: Optional[str] = None
    category: Optional[str] = None  # installation, usage, api, etc.


def generate_qa_pairs(parsed_readmes: List[ParsedReadme]) -> List[QAPair]:
    """
    Generate Q&A pairs from parsed README files.
    
    This function analyzes all parsed README content and generates comprehensive
    question-answer pairs covering:
    - Installation questions
    - Usage questions
    - API questions
    - Troubleshooting questions
    - Code examples
    - Commands
    - Configuration
    
    Args:
        parsed_readmes: List of ParsedReadme objects from the parser
    
    Returns:
        List of QAPair objects
    """
    all_qa_pairs = []
    
    for parsed_readme in parsed_readmes:
        # Generate Q&A from each section
        for section in _flatten_sections(parsed_readmes):
            section_qa = _generate_section_qa(section)
            all_qa_pairs.extend(section_qa)
        
        # Generate Q&A from code blocks
        if QA_CONFIG.get("generate_from_code_blocks", True):
            code_qa = _generate_code_block_qa(parsed_readme.code_blocks, parsed_readme.file_name)
            all_qa_pairs.extend(code_qa)
        
        # Generate Q&A from tables
        if QA_CONFIG.get("generate_from_tables", True):
            table_qa = _generate_table_qa(parsed_readme.tables, parsed_readme.file_name)
            all_qa_pairs.extend(table_qa)
        
        # Generate Q&A from workflows
        if QA_CONFIG.get("include_workflow_qa", True):
            workflow_qa = _generate_workflow_qa(parsed_readme.workflows, parsed_readme.file_name)
            all_qa_pairs.extend(workflow_qa)
    
    # Remove duplicates and limit per section
    all_qa_pairs = _deduplicate_qa_pairs(all_qa_pairs)
    all_qa_pairs = _limit_qa_per_category(all_qa_pairs)
    
    return all_qa_pairs


def format_qa_section(qa_pairs: List[QAPair], style: Optional[str] = None) -> str:
    """
    Format Q&A pairs as markdown section.
    
    Supports multiple formatting styles:
    - "collapsible": HTML details/summary (for GitHub)
    - "simple": Q: A: format
    - "numbered": Numbered list format
    
    Args:
        qa_pairs: List of QAPair objects to format
        style: Formatting style (defaults to OUTPUT_CONFIG["qa_section_style"])
    
    Returns:
        Formatted markdown string
    """
    if not qa_pairs:
        return ""
    
    if style is None:
        style = OUTPUT_CONFIG.get("qa_section_style", "simple")
    
    # Group by category
    qa_by_category = _group_qa_by_category(qa_pairs)
    
    # Format header
    markdown = "## Frequently Asked Questions\n\n"
    
    # Format each category
    for category, pairs in qa_by_category.items():
        if category and category != "unknown":
            markdown += f"### {category.title()} Questions\n\n"
        
        # Format pairs based on style
        if style == "collapsible":
            markdown += _format_collapsible_qa(pairs)
        elif style == "numbered":
            markdown += _format_numbered_qa(pairs)
        else:  # simple
            markdown += _format_simple_qa(pairs)
        
        markdown += "\n"
    
    return markdown


# ============================================================================
# Q&A Generation Functions
# ============================================================================

def _generate_section_qa(section: Section) -> List[QAPair]:
    """Generate Q&A pairs from a section."""
    qa_pairs = []
    section_type = section.section_type
    
    # Skip if section type is not configured for Q&A
    config_key = f"include_{section_type}_qa"
    if not QA_CONFIG.get(config_key, True) and section_type != "unknown":
        return qa_pairs
    
    # Extract key concepts and actions from content
    concepts = _extract_concepts(section.content)
    actions = _extract_actions(section.content)
    commands = _extract_commands(section.content)
    
    # Generate questions from concepts
    for concept in concepts[:5]:  # Limit to 5 concepts
        question = _generate_question_from_concept(concept, section_type)
        answer = _generate_answer_from_content(concept, section.content, section_type)
        if question and answer:
            qa_pairs.append(QAPair(
                question=question,
                answer=answer,
                section_type=section_type,
                source_section=section.title,
                category=section_type
            ))
    
    # Generate questions from actions
    for action in actions[:5]:  # Limit to 5 actions
        question = _generate_question_from_action(action, section_type)
        answer = _generate_answer_from_content(action, section.content, section_type)
        if question and answer:
            qa_pairs.append(QAPair(
                question=question,
                answer=answer,
                section_type=section_type,
                source_section=section.title,
                category=section_type
            ))
    
    # Generate questions from commands
    if QA_CONFIG.get("generate_from_commands", True):
        for command in commands[:3]:  # Limit to 3 commands
            question = _generate_question_from_command(command, section_type)
            answer = _generate_answer_from_command(command, section.content)
            if question and answer:
                qa_pairs.append(QAPair(
                    question=question,
                    answer=answer,
                    section_type=section_type,
                    source_section=section.title,
                    category=section_type
                ))
    
    # Limit questions per section
    min_q = QA_CONFIG.get("min_questions_per_section", 3)
    max_q = QA_CONFIG.get("max_questions_per_section", 10)
    
    if len(qa_pairs) < min_q:
        # Generate additional generic questions
        additional = _generate_generic_qa(section, min_q - len(qa_pairs))
        qa_pairs.extend(additional)
    
    return qa_pairs[:max_q]


def _generate_code_block_qa(code_blocks: List[CodeBlock], source: str) -> List[QAPair]:
    """Generate Q&A pairs from code blocks."""
    qa_pairs = []
    
    for code_block in code_blocks:
        if code_block.is_inline:
            continue
        
        # Generate question about what the code does
        question = f"What does this {code_block.language or 'code'} code do?"
        answer = _explain_code_block(code_block)
        
        if answer:
            qa_pairs.append(QAPair(
                question=question,
                answer=answer,
                section_type="examples",
                source_section=source,
                category="code"
            ))
        
        # Generate question about how to run/use the code
        if code_block.language in ["bash", "sh", "shell", "console"]:
            question = f"How do I run this command?"
            answer = f"Run the following command:\n\n```{code_block.language}\n{code_block.content}\n```"
            
            qa_pairs.append(QAPair(
                question=question,
                answer=answer,
                section_type="usage",
                source_section=source,
                category="commands"
            ))
    
    return qa_pairs


def _generate_table_qa(tables: List[str], source: str) -> List[QAPair]:
    """Generate Q&A pairs from table content."""
    qa_pairs = []
    
    for table in tables[:3]:  # Limit to 3 tables
        # Extract table headers
        lines = table.split('\n')
        if len(lines) >= 2:
            headers = [h.strip() for h in lines[0].split('|') if h.strip()]
            
            if headers:
                question = f"What information is in the {headers[0]} table?"
                answer = f"The table contains the following columns: {', '.join(headers)}.\n\n{table}"
                
                qa_pairs.append(QAPair(
                    question=question,
                    answer=answer,
                    section_type="unknown",
                    source_section=source,
                    category="reference"
                ))
    
    return qa_pairs


def _generate_workflow_qa(workflows: List[str], source: str) -> List[QAPair]:
    """Generate Q&A pairs from workflow content."""
    qa_pairs = []
    
    for workflow in workflows[:2]:  # Limit to 2 workflows
        # Extract steps
        steps = re.findall(r"^\d+\.\s+(.+)$", workflow, re.MULTILINE)
        
        if steps:
            question = "What are the steps in this workflow?"
            answer = f"Here are the steps:\n\n{workflow}"
            
            qa_pairs.append(QAPair(
                question=question,
                answer=answer,
                section_type="workflow",
                source_section=source,
                category="workflow"
            ))
    
    return qa_pairs


# ============================================================================
# Content Extraction Functions
# ============================================================================

def _extract_concepts(content: str) -> List[str]:
    """Extract key concepts (nouns, technical terms) from content."""
    concepts = []
    
    # Extract technical terms (capitalized acronyms and multi-word terms)
    tech_terms = re.findall(r'\b[A-Z]{2,}\b', content)  # RADP, API, etc.
    concepts.extend(tech_terms)
    
    # Extract capitalized multi-word terms (likely technical concepts)
    capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', content)
    concepts.extend(capitalized)
    
    # Extract quoted terms
    quoted = re.findall(r'"([^"]+)"', content)
    concepts.extend(quoted)
    
    # Extract terms in backticks (code/technical terms)
    backticked = re.findall(r'`([^`]+)`', content)
    concepts.extend(backticked)
    
    # Extract common technical nouns (API, model, service, etc.)
    tech_nouns = re.findall(r'\b(?:API|model|service|client|server|container|docker|python|radp|maveric|simulation|training|prediction)\b', content, re.IGNORECASE)
    concepts.extend(tech_nouns)
    
    # Remove duplicates and filter
    concepts = list(set(concepts))
    # Filter out common words and very short/long terms
    stop_words = {"the", "and", "for", "with", "this", "that", "from", "are", "can", "will", "you", "your"}
    concepts = [
        c for c in concepts 
        if 3 < len(c) < 50 
        and c.lower() not in stop_words
        and not c.isdigit()
    ]
    
    return concepts[:10]  # Return top 10


def _extract_actions(content: str) -> List[str]:
    """Extract actions (verbs, commands) from content."""
    actions = []
    
    # Extract imperative verbs (commands)
    imperative_patterns = [
        r'(?:run|install|start|stop|create|set|use|configure|test|build)\s+([a-z]+(?:\s+[a-z]+)*)',
        r'(?:to|for)\s+([a-z]+(?:\s+[a-z]+)*)',
    ]
    
    for pattern in imperative_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        actions.extend(matches)
    
    # Extract from "How to" patterns
    how_to = re.findall(r'how\s+to\s+([a-z]+(?:\s+[a-z]+)*)', content, re.IGNORECASE)
    actions.extend(how_to)
    
    # Remove duplicates
    actions = list(set(actions))
    actions = [a for a in actions if len(a) > 2]
    
    return actions[:10]


def _extract_commands(content: str) -> List[str]:
    """Extract commands from code blocks."""
    commands = []
    
    # Extract from code blocks
    code_pattern = r"```(?:bash|sh|shell|console)?\n(.*?)\n```"
    code_blocks = re.findall(code_pattern, content, re.DOTALL)
    
    for code_block in code_blocks:
        lines = code_block.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                commands.append(line)
    
    return commands[:10]


# ============================================================================
# Question Generation Functions
# ============================================================================

def _generate_question_from_concept(concept: str, section_type: str) -> str:
    """Generate a question from a concept."""
    # Clean and normalize concept
    concept_clean = concept.strip()
    if len(concept_clean) > 60:  # Too long, truncate
        concept_clean = concept_clean[:60] + "..."
    
    # Select appropriate template based on section type
    if section_type == "installation":
        if "install" in concept_clean.lower() or "setup" in concept_clean.lower():
            return f"How do I {concept_clean.lower()}?"
        return f"What is {concept_clean.lower()}?"
    elif section_type == "usage":
        return f"How do I use {concept_clean.lower()}?"
    elif section_type == "api":
        if "API" in concept_clean:
            return f"What is the {concept_clean.lower()}?"
        return f"What is the {concept_clean.lower()} API?"
    elif section_type == "troubleshooting":
        return f"How to troubleshoot {concept_clean.lower()}?"
    else:
        # Generic question
        return f"What is {concept_clean.lower()}?"


def _generate_question_from_action(action: str, section_type: str) -> str:
    """Generate a question from an action."""
    templates = QA_CONFIG.get("question_templates", [])
    
    if section_type == "installation":
        template = "How do I {action}?"
    elif section_type == "usage":
        template = "How to {action}?"
    elif section_type == "troubleshooting":
        template = "How to troubleshoot {action}?"
    else:
        template = "How do I {action}?"
    
    return template.format(action=action.lower())


def _generate_question_from_command(command: str, section_type: str) -> str:
    """Generate a question from a command."""
    # Extract command name
    cmd_parts = command.split()
    if cmd_parts:
        cmd_name = cmd_parts[0]
        return f"How to run {cmd_name}?"
    
    return f"How do I run this command?"


def _generate_answer_from_content(concept_or_action: str, content: str, section_type: str) -> str:
    """Generate an answer from content for a concept or action."""
    # Normalize search term
    search_term = concept_or_action.lower()
    
    # Find relevant sentences containing the concept/action
    sentences = re.split(r'[.!?]\s+', content)
    relevant_sentences = []
    
    for sentence in sentences:
        sentence_lower = sentence.lower()
        # Check if sentence contains the concept/action
        if search_term in sentence_lower and len(sentence.strip()) > 20:
            # Prioritize sentences that start with or contain the term
            if sentence_lower.startswith(search_term) or sentence_lower.find(search_term) < 50:
                relevant_sentences.insert(0, sentence.strip())
            else:
                relevant_sentences.append(sentence.strip())
    
    if relevant_sentences:
        # Use first 2-3 most relevant sentences
        answer = '. '.join(relevant_sentences[:3])
        if not answer.endswith('.'):
            answer += '.'
        # Clean up answer
        answer = re.sub(r'\s+', ' ', answer)  # Remove extra whitespace
        return answer
    
    # Try to find code blocks related to the concept
    code_pattern = r"```[\w]*\n(.*?)\n```"
    code_blocks = re.findall(code_pattern, content, re.DOTALL)
    for code_block in code_blocks:
        if search_term in code_block.lower():
            return f"Here's how to work with {concept_or_action}:\n\n```\n{code_block[:200]}\n```"
    
    # Fallback: generate generic answer
    return _generate_generic_answer(concept_or_action, section_type)


def _generate_answer_from_command(command: str, content: str) -> str:
    """Generate an answer explaining a command."""
    # Find context around the command
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if command in line:
            # Get surrounding context
            context_start = max(0, i - 2)
            context_end = min(len(lines), i + 3)
            context = '\n'.join(lines[context_start:context_end])
            
            return f"To run this command:\n\n```bash\n{command}\n```\n\n{context}"
    
    return f"Run the following command:\n\n```bash\n{command}\n```"


def _generate_generic_answer(concept: str, section_type: str) -> str:
    """Generate a generic answer when specific content isn't found."""
    if section_type == "installation":
        return f"To install or set up {concept}, follow the installation instructions in the README."
    elif section_type == "usage":
        return f"To use {concept}, refer to the usage examples in the documentation."
    elif section_type == "api":
        return f"The {concept} API is documented in the API reference section."
    else:
        return f"Information about {concept} can be found in the documentation."


def _generate_generic_qa(section: Section, count: int) -> List[QAPair]:
    """Generate generic Q&A pairs for a section."""
    qa_pairs = []
    templates = QA_CONFIG.get("question_templates", [])
    
    # Extract key terms from section title and content
    title_words = section.title.split()
    key_terms = [w for w in title_words if len(w) > 4][:3]
    
    for i in range(count):
        if i < len(templates) and key_terms:
            template = templates[i % len(templates)]
            term = key_terms[i % len(key_terms)]
            
            # Fill template
            if "{action}" in template:
                question = template.format(action=f"use {term}")
            elif "{concept}" in template:
                question = template.format(concept=term)
            elif "{feature}" in template:
                question = template.format(feature=term)
            else:
                question = f"What is {term}?"
            
            answer = _generate_answer_from_content(term, section.content, section.section_type)
            
            qa_pairs.append(QAPair(
                question=question,
                answer=answer,
                section_type=section.section_type,
                source_section=section.title,
                category=section.section_type
            ))
    
    return qa_pairs


# ============================================================================
# Answer Generation Helper Functions
# ============================================================================

def _explain_code_block(code_block: CodeBlock) -> str:
    """Explain what a code block does."""
    content = code_block.content
    language = code_block.language or "code"
    
    # Analyze code to generate explanation
    if "import" in content or "from" in content:
        return f"This {language} code imports required modules and dependencies."
    elif "def" in content or "function" in content:
        return f"This {language} code defines functions for specific operations."
    elif "docker" in content.lower():
        return f"This command manages Docker containers and services."
    elif "pip" in content.lower() or "install" in content.lower():
        return f"This command installs Python packages and dependencies."
    elif "python" in content.lower():
        return f"This command runs a Python script or application."
    else:
        return f"This {language} code performs operations as specified in the documentation."


# ============================================================================
# Formatting Functions
# ============================================================================

def _format_simple_qa(qa_pairs: List[QAPair]) -> str:
    """Format Q&A pairs in simple Q: A: format."""
    markdown = ""
    
    for qa in qa_pairs:
        markdown += f"**Q: {qa.question}**\n\n"
        markdown += f"A: {qa.answer}\n\n"
        markdown += "---\n\n"
    
    return markdown


def _format_collapsible_qa(qa_pairs: List[QAPair]) -> str:
    """Format Q&A pairs in collapsible HTML format (GitHub compatible)."""
    markdown = ""
    
    for qa in qa_pairs:
        markdown += f"<details>\n<summary><b>{qa.question}</b></summary>\n\n"
        markdown += f"{qa.answer}\n\n"
        markdown += "</details>\n\n"
    
    return markdown


def _format_numbered_qa(qa_pairs: List[QAPair]) -> str:
    """Format Q&A pairs as numbered list."""
    markdown = ""
    
    for i, qa in enumerate(qa_pairs, 1):
        markdown += f"{i}. **{qa.question}**\n\n"
        markdown += f"   {qa.answer}\n\n"
    
    return markdown


# ============================================================================
# Utility Functions
# ============================================================================

def _flatten_sections(parsed_readmes: List[ParsedReadme]) -> List[Section]:
    """Flatten all sections from all parsed READMEs."""
    from readme_generator.parser import get_all_sections_flat
    
    all_sections = []
    for parsed_readme in parsed_readmes:
        all_sections.extend(get_all_sections_flat(parsed_readme.sections))
    
    return all_sections


def _group_qa_by_category(qa_pairs: List[QAPair]) -> Dict[str, List[QAPair]]:
    """Group Q&A pairs by category."""
    grouped = {}
    
    for qa in qa_pairs:
        category = qa.category or qa.section_type or "general"
        if category not in grouped:
            grouped[category] = []
        grouped[category].append(qa)
    
    return grouped


def _deduplicate_qa_pairs(qa_pairs: List[QAPair]) -> List[QAPair]:
    """Remove duplicate Q&A pairs."""
    seen_questions = set()
    unique_pairs = []
    
    for qa in qa_pairs:
        # Normalize question for comparison
        question_lower = qa.question.lower().strip()
        if question_lower not in seen_questions:
            seen_questions.add(question_lower)
            unique_pairs.append(qa)
    
    return unique_pairs


def _limit_qa_per_category(qa_pairs: List[QAPair]) -> List[QAPair]:
    """Limit number of Q&A pairs per category."""
    grouped = _group_qa_by_category(qa_pairs)
    max_per_category = QA_CONFIG.get("max_questions_per_section", 10)
    
    limited = []
    for category, pairs in grouped.items():
        limited.extend(pairs[:max_per_category])
    
    return limited

