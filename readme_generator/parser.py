"""
Markdown parser for README files.

This module provides functions to parse README markdown files and extract:
- Sections with hierarchy
- Code blocks (inline and fenced)
- Tables
- Links
- Workflows
- Special content (mermaid diagrams, version info, etc.)
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from readme_generator.config import (
    SOURCE_README_DIR,
    SECTION_HEADERS,
    HEADER_PATTERNS,
    SECTION_DETECTION_PATTERNS,
    CODE_BLOCK_CONFIG,
    TABLE_CONFIG,
    LINK_CONFIG,
    SPECIAL_CONTENT_CONFIG,
    NESTING_CONFIG,
    EDGE_CASE_CONFIG,
    get_section_type_from_header,
    should_process_file,
)


@dataclass
class CodeBlock:
    """Represents a code block in markdown."""
    content: str
    language: Optional[str] = None
    is_inline: bool = False
    line_number: Optional[int] = None


@dataclass
class Section:
    """Represents a section in markdown."""
    title: str
    level: int  # 1-6 for # through ######
    content: str
    section_type: str = "unknown"  # installation, usage, api, etc.
    subsections: List['Section'] = field(default_factory=list)
    code_blocks: List[CodeBlock] = field(default_factory=list)
    tables: List[str] = field(default_factory=list)
    links: List[Dict[str, str]] = field(default_factory=list)
    line_number: Optional[int] = None


@dataclass
class ParsedReadme:
    """Represents a parsed README file."""
    file_path: Path
    file_name: str
    title: Optional[str] = None
    sections: List[Section] = field(default_factory=list)
    code_blocks: List[CodeBlock] = field(default_factory=list)
    tables: List[str] = field(default_factory=list)
    links: List[Dict[str, str]] = field(default_factory=list)
    workflows: List[str] = field(default_factory=list)
    special_content: Dict[str, List[str]] = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)


def parse_readme(file_path: Path) -> ParsedReadme:
    """
    Parse a single README markdown file and extract structured information.
    
    Args:
        file_path: Path to the markdown file
    
    Returns:
        ParsedReadme object containing all extracted information
    
    Raises:
        FileNotFoundError: If file doesn't exist
        UnicodeDecodeError: If file encoding is not supported
    """
    # Validate file
    if not should_process_file(file_path):
        raise ValueError(f"File {file_path} should not be processed based on config")
    
    # Read file with encoding handling
    content = _read_file_with_encoding(file_path)
    lines = content.split('\n')
    
    # Initialize parsed readme
    parsed = ParsedReadme(
        file_path=file_path,
        file_name=file_path.name
    )
    
    # Extract title (first H1 or filename)
    parsed.title = _extract_title(lines)
    
    # Extract all code blocks first (to exclude from section parsing)
    parsed.code_blocks = _extract_code_blocks(content, lines)
    
    # Extract tables
    parsed.tables = _extract_tables(lines)
    
    # Extract links
    parsed.links = _extract_links(content)
    
    # Extract special content
    parsed.special_content = _extract_special_content(content)
    
    # Extract workflows
    parsed.workflows = _extract_workflows(content, lines)
    
    # Parse sections with hierarchy
    parsed.sections = _parse_sections(lines, content)
    
    # Add metadata
    parsed.metadata = {
        "total_lines": len(lines),
        "total_sections": len(parsed.sections),
        "total_code_blocks": len(parsed.code_blocks),
        "total_tables": len(parsed.tables),
        "total_links": len(parsed.links),
        "has_mermaid": "mermaid" in parsed.special_content,
        "has_version": "version" in parsed.special_content,
    }
    
    return parsed


def parse_all_readmes(source_dir: Optional[Path] = None) -> List[ParsedReadme]:
    """
    Parse all README files in the source directory.
    
    Args:
        source_dir: Directory containing README files. Defaults to SOURCE_README_DIR from config.
    
    Returns:
        List of ParsedReadme objects, one for each README file
    
    Raises:
        FileNotFoundError: If source directory doesn't exist
    """
    if source_dir is None:
        source_dir = SOURCE_README_DIR
    
    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory does not exist: {source_dir}")
    
    parsed_readmes = []
    
    # Find all markdown files
    md_files = []
    for ext in [".md", ".MD", ".Md", ".mD"]:
        md_files.extend(list(source_dir.glob(f"*{ext}")))
    
    # Remove duplicates and filter
    md_files = list(set(md_files))
    md_files = [f for f in md_files if should_process_file(f)]
    
    # Sort for consistent processing
    md_files.sort(key=lambda x: x.name.lower())
    
    # Parse each file
    for file_path in md_files:
        try:
            parsed = parse_readme(file_path)
            parsed_readmes.append(parsed)
        except Exception as e:
            # Log error but continue with other files
            print(f"Warning: Failed to parse {file_path}: {e}")
            continue
    
    return parsed_readmes


def _read_file_with_encoding(file_path: Path) -> str:
    """Read file with encoding fallback."""
    encodings = [EDGE_CASE_CONFIG.get("preferred_encoding", "utf-8")]
    encodings.extend(EDGE_CASE_CONFIG.get("fallback_encodings", []))
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    
    # If all encodings fail, try with error handling
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        return f.read()


def _extract_title(lines: List[str]) -> Optional[str]:
    """Extract title from first H1 header or filename."""
    # Look for first H1
    h1_pattern = re.compile(HEADER_PATTERNS["h1"])
    for line in lines[:20]:  # Check first 20 lines
        match = h1_pattern.match(line)
        if match:
            title = line.lstrip('#').strip()
            return title
    
    return None


def _extract_code_blocks(content: str, lines: List[str]) -> List[CodeBlock]:
    """Extract all code blocks (both inline and fenced)."""
    code_blocks = []
    
    # Extract fenced code blocks (```code```)
    fenced_pattern = re.compile(
        r"```(\w+)?\n(.*?)```",
        re.DOTALL | re.MULTILINE
    )
    
    for match in fenced_pattern.finditer(content):
        language = match.group(1) if match.group(1) else None
        code_content = match.group(2).strip()
        
        # Skip if too short
        if len(code_content) < CODE_BLOCK_CONFIG.get("min_code_block_length", 10):
            continue
        
        # Find line number
        line_num = content[:match.start()].count('\n') + 1
        
        code_blocks.append(CodeBlock(
            content=code_content,
            language=language,
            is_inline=False,
            line_number=line_num
        ))
    
    # Extract inline code (`code`)
    inline_pattern = re.compile(CODE_BLOCK_CONFIG["inline_code_pattern"])
    for match in inline_pattern.finditer(content):
        code_content = match.group(0).strip('`')
        
        # Skip if too short or just punctuation
        if len(code_content) < 2 or code_content in ['', ' ']:
            continue
        
        line_num = content[:match.start()].count('\n') + 1
        
        code_blocks.append(CodeBlock(
            content=code_content,
            language=None,
            is_inline=True,
            line_number=line_num
        ))
    
    return code_blocks


def _extract_tables(lines: List[str]) -> List[str]:
    """Extract markdown tables."""
    if not TABLE_CONFIG.get("detect_tables", True):
        return []
    
    tables = []
    table_lines = []
    in_table = False
    
    for i, line in enumerate(lines):
        # Check if line is a table row
        if re.match(TABLE_CONFIG["table_pattern"], line):
            if not in_table:
                in_table = True
                # Check if previous line was also a table row (for multi-line tables)
                if i > 0 and re.match(TABLE_CONFIG["table_pattern"], lines[i-1]):
                    table_lines = [lines[i-1]]
            table_lines.append(line)
        elif re.match(TABLE_CONFIG["table_separator_pattern"], line):
            # Table separator row
            if in_table:
                table_lines.append(line)
        else:
            # End of table
            if in_table and table_lines:
                tables.append('\n'.join(table_lines))
                table_lines = []
            in_table = False
    
    # Handle table at end of file
    if in_table and table_lines:
        tables.append('\n'.join(table_lines))
    
    return tables


def _extract_links(content: str) -> List[Dict[str, str]]:
    """Extract all links from markdown."""
    links = []
    
    if not LINK_CONFIG.get("detect_markdown_links", True):
        return links
    
    # Extract markdown links [text](url)
    link_pattern = re.compile(LINK_CONFIG["link_pattern"])
    for match in link_pattern.finditer(content):
        text = match.group(1)
        url = match.group(2)
        
        link_type = "external"
        if url.startswith('#'):
            link_type = "anchor"
        elif url.startswith('http://') or url.startswith('https://'):
            link_type = "external"
        else:
            link_type = "file"
        
        links.append({
            "text": text,
            "url": url,
            "type": link_type
        })
    
    return links


def _extract_special_content(content: str) -> Dict[str, List[str]]:
    """Extract special content like mermaid diagrams, version info, dates."""
    special = {}
    
    # Extract mermaid diagrams
    if SPECIAL_CONTENT_CONFIG.get("detect_mermaid_diagrams", True):
        mermaid_pattern = re.compile(SPECIAL_CONTENT_CONFIG["mermaid_pattern"], re.MULTILINE | re.DOTALL)
        mermaid_diagrams = mermaid_pattern.findall(content)
        if mermaid_diagrams:
            special["mermaid"] = mermaid_diagrams
    
    # Extract version info
    if SPECIAL_CONTENT_CONFIG.get("detect_version_info", True):
        version_pattern = re.compile(SPECIAL_CONTENT_CONFIG["version_pattern"], re.IGNORECASE)
        versions = version_pattern.findall(content)
        if versions:
            special["version"] = versions
    
    # Extract dates
    if SPECIAL_CONTENT_CONFIG.get("detect_dates", True):
        date_pattern = re.compile(SPECIAL_CONTENT_CONFIG["date_pattern"], re.IGNORECASE)
        dates = date_pattern.findall(content)
        if dates:
            special["dates"] = dates
    
    # Extract images
    if SPECIAL_CONTENT_CONFIG.get("detect_images", True):
        image_pattern = re.compile(r"!\[([^\]]*)\]\(([^\)]+)\)")
        images = image_pattern.findall(content)
        if images:
            special["images"] = [{"alt": alt, "url": url} for alt, url in images]
    
    return special


def _extract_workflows(content: str, lines: List[str]) -> List[str]:
    """Extract workflow descriptions (step-by-step processes)."""
    workflows = []
    
    # Look for numbered lists that might be workflows
    workflow_pattern = re.compile(r"^\d+\.\s+.+", re.MULTILINE)
    workflow_items = []
    current_workflow = []
    
    for i, line in enumerate(lines):
        match = workflow_pattern.match(line)
        if match:
            current_workflow.append(line.strip())
        else:
            if current_workflow and len(current_workflow) >= 3:  # At least 3 steps
                workflows.append('\n'.join(current_workflow))
                current_workflow = []
    
    # Handle workflow at end
    if current_workflow and len(current_workflow) >= 3:
        workflows.append('\n'.join(current_workflow))
    
    # Also look for sections with "workflow" or "pipeline" in title
    workflow_sections = []
    for i, line in enumerate(lines):
        if re.match(r"^#{1,6}\s+.*(workflow|pipeline|process|steps)", line, re.IGNORECASE):
            # Extract content until next header
            section_content = []
            for j in range(i + 1, len(lines)):
                if re.match(r"^#{1,6}\s+", lines[j]):
                    break
                section_content.append(lines[j])
            if section_content:
                workflow_sections.append('\n'.join(section_content))
    
    workflows.extend(workflow_sections)
    
    return workflows


def _parse_sections(lines: List[str], content: str) -> List[Section]:
    """Parse markdown sections with hierarchy."""
    sections = []
    current_section = None
    current_content = []
    current_level = 0
    
    for i, line in enumerate(lines):
        # Check if line is a header
        header_match = _match_header(line)
        
        if header_match:
            # Save previous section
            if current_section is not None:
                current_section.content = '\n'.join(current_content).strip()
                sections.append(current_section)
            
            # Start new section
            level, title = header_match
            section_type = get_section_type_from_header(line)
            
            current_section = Section(
                title=title,
                level=level,
                content="",
                section_type=section_type,
                line_number=i + 1
            )
            current_content = []
            current_level = level
            
        else:
            # Add to current section content
            if current_section is not None:
                current_content.append(line)
            elif not sections:  # Content before first header
                # This is preamble/title area
                pass
    
    # Save last section
    if current_section is not None:
        current_section.content = '\n'.join(current_content).strip()
        sections.append(current_section)
    
    # Build hierarchy (parent-child relationships)
    sections = _build_section_hierarchy(sections)
    
    # Extract code blocks and tables for each section
    for section in sections:
        section.code_blocks = _extract_section_code_blocks(section.content)
        section.tables = _extract_section_tables(section.content)
        section.links = _extract_section_links(section.content)
    
    return sections


def _match_header(line: str) -> Optional[Tuple[int, str]]:
    """Match a header line and return (level, title) or None."""
    # Match any header level
    for level in range(1, NESTING_CONFIG.get("max_nesting_depth", 6) + 1):
        pattern = f"^{'#' * level}\\s+(.+)$"
        match = re.match(pattern, line)
        if match:
            title = match.group(1).strip()
            # Remove numbering if present (e.g., "1. Title" -> "Title")
            title = re.sub(r"^\d+\.\s+", "", title)
            return (level, title)
    
    return None


def _build_section_hierarchy(sections: List[Section]) -> List[Section]:
    """Build parent-child relationships between sections."""
    if not sections:
        return sections
    
    # Root sections (no parent)
    root_sections = []
    section_stack = []  # Stack to track parent sections
    
    for section in sections:
        # Pop sections from stack that are at same or higher level
        while section_stack and section_stack[-1].level >= section.level:
            section_stack.pop()
        
        # Add to parent's subsections if parent exists
        if section_stack:
            section_stack[-1].subsections.append(section)
        else:
            root_sections.append(section)
        
        # Push current section to stack
        section_stack.append(section)
    
    return root_sections


def _extract_section_code_blocks(content: str) -> List[CodeBlock]:
    """Extract code blocks from a section's content."""
    code_blocks = []
    
    # Fenced code blocks
    fenced_pattern = re.compile(r"```(\w+)?\n(.*?)```", re.DOTALL)
    for match in fenced_pattern.finditer(content):
        language = match.group(1) if match.group(1) else None
        code_content = match.group(2).strip()
        
        if len(code_content) >= CODE_BLOCK_CONFIG.get("min_code_block_length", 10):
            code_blocks.append(CodeBlock(
                content=code_content,
                language=language,
                is_inline=False
            ))
    
    # Inline code
    inline_pattern = re.compile(CODE_BLOCK_CONFIG["inline_code_pattern"])
    for match in inline_pattern.finditer(content):
        code_content = match.group(0).strip('`')
        if len(code_content) >= 2:
            code_blocks.append(CodeBlock(
                content=code_content,
                language=None,
                is_inline=True
            ))
    
    return code_blocks


def _extract_section_tables(content: str) -> List[str]:
    """Extract tables from a section's content."""
    lines = content.split('\n')
    tables = []
    table_lines = []
    in_table = False
    
    for line in lines:
        if re.match(TABLE_CONFIG["table_pattern"], line):
            if not in_table:
                in_table = True
            table_lines.append(line)
        elif re.match(TABLE_CONFIG["table_separator_pattern"], line):
            if in_table:
                table_lines.append(line)
        else:
            if in_table and table_lines:
                tables.append('\n'.join(table_lines))
                table_lines = []
            in_table = False
    
    if in_table and table_lines:
        tables.append('\n'.join(table_lines))
    
    return tables


def _extract_section_links(content: str) -> List[Dict[str, str]]:
    """Extract links from a section's content."""
    links = []
    link_pattern = re.compile(LINK_CONFIG["link_pattern"])
    
    for match in link_pattern.finditer(content):
        text = match.group(1)
        url = match.group(2)
        
        link_type = "external"
        if url.startswith('#'):
            link_type = "anchor"
        elif url.startswith('http://') or url.startswith('https://'):
            link_type = "external"
        else:
            link_type = "file"
        
        links.append({
            "text": text,
            "url": url,
            "type": link_type
        })
    
    return links


def count_all_sections(sections: List[Section]) -> int:
    """
    Count all sections including nested subsections.
    
    Args:
        sections: List of Section objects (may have nested subsections)
    
    Returns:
        Total count of all sections including nested ones
    """
    count = len(sections)
    for section in sections:
        count += count_all_sections(section.subsections)
    return count


def get_all_sections_flat(sections: List[Section]) -> List[Section]:
    """
    Flatten section hierarchy into a flat list.
    
    Args:
        sections: List of Section objects with nested subsections
    
    Returns:
        Flat list of all sections (depth-first order)
    """
    flat = []
    for section in sections:
        flat.append(section)
        flat.extend(get_all_sections_flat(section.subsections))
    return flat

