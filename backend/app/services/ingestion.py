"""
Data Ingestion Service.

Responsible for:
1. Loading Markdown source documents from disk.
2. Parsing [SourceID: X] anchors to build a citation index.
3. Chunking text for vector store embedding (Phase 2).
4. Providing citation lookup for the API layer.
"""

import re
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

from app.core.config import get_settings

# --- Data Structures ---

@dataclass
class Citation:
    """A single citable paragraph anchored by a SourceID."""
    source_id: str
    text: str
    document_name: str
    section_heading: str


@dataclass
class DocumentChunk:
    """A chunk of text from a document, ready for embedding."""
    chunk_id: str
    text: str
    document_name: str
    source_ids: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


@dataclass
class DocumentMetadata:
    """Metadata about an ingested document."""
    filename: str
    title: str
    total_citations: int
    sections: list[str]


# --- Module-Level State ---
_citation_index: dict[str, Citation] = {}
_document_metadata: list[DocumentMetadata] = []
_document_chunks: list[DocumentChunk] = []
_is_loaded: bool = False

# --- Regex Patterns ---
SOURCE_ID_PATTERN = re.compile(r"\[SourceID:\s*([^\]]+)\]")
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)


def _extract_title(content: str) -> str:
    """Extract the first H1 heading as the document title."""
    match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    return match.group(1).strip() if match else "Untitled"


def _extract_sections(content: str) -> list[str]:
    """Extract all H2 section headings from the document."""
    return [m.group(2).strip() for m in HEADING_PATTERN.finditer(content) if len(m.group(1)) == 2]


def _get_current_heading(content: str, position: int) -> str:
    """Find the most recent heading before a given position in the text."""
    headings = list(HEADING_PATTERN.finditer(content))
    current = "Introduction"
    for h in headings:
        if h.start() < position:
            current = h.group(2).strip()
        else:
            break
    return current


def _parse_citations(content: str, document_name: str) -> dict[str, Citation]:
    """
    Parse all [SourceID: X] tags from the content.
    
    For each SourceID found, capture the paragraph text that follows it
    (up to the next SourceID, heading, or horizontal rule).
    """
    citations = {}
    matches = list(SOURCE_ID_PATTERN.finditer(content))

    for i, match in enumerate(matches):
        source_id = match.group(1).strip()
        start = match.end()

        # End boundary: next SourceID, next heading, next HR, or end of content
        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            end = len(content)

        # Extract the paragraph text
        raw_text = content[start:end].strip()

        # Clean: stop at the next heading or horizontal rule
        clean_lines = []
        for line in raw_text.split("\n"):
            stripped = line.strip()
            if stripped.startswith("#") or stripped == "---":
                break
            clean_lines.append(line)

        text = "\n".join(clean_lines).strip()

        # Remove any trailing SourceID remnants
        text = SOURCE_ID_PATTERN.sub("", text).strip()

        if text:
            section = _get_current_heading(content, match.start())
            citations[source_id] = Citation(
                source_id=source_id,
                text=text,
                document_name=document_name,
                section_heading=section,
            )

    return citations


def _chunk_document(content: str, document_name: str, chunk_size: int = 800) -> list[DocumentChunk]:
    """
    Split document content into chunks for vector embedding.
    
    Strategy: Split by sections (## headings), then by paragraph if too long.
    Each chunk retains references to its contained SourceIDs.
    """
    chunks = []
    sections = re.split(r"\n(?=##\s)", content)

    for section_idx, section in enumerate(sections):
        # Find all SourceIDs in this section
        source_ids = SOURCE_ID_PATTERN.findall(section)

        # If section is small enough, keep as one chunk
        if len(section) <= chunk_size:
            chunk_id = f"{document_name}::chunk_{section_idx}"
            chunks.append(DocumentChunk(
                chunk_id=chunk_id,
                text=section.strip(),
                document_name=document_name,
                source_ids=source_ids,
            ))
        else:
            # Split by paragraphs (double newline)
            paragraphs = section.split("\n\n")
            current_chunk = ""
            current_ids = []
            sub_idx = 0

            for para in paragraphs:
                para_ids = SOURCE_ID_PATTERN.findall(para)

                if len(current_chunk) + len(para) > chunk_size and current_chunk:
                    chunk_id = f"{document_name}::chunk_{section_idx}_{sub_idx}"
                    chunks.append(DocumentChunk(
                        chunk_id=chunk_id,
                        text=current_chunk.strip(),
                        document_name=document_name,
                        source_ids=current_ids,
                    ))
                    current_chunk = para
                    current_ids = para_ids
                    sub_idx += 1
                else:
                    current_chunk += "\n\n" + para if current_chunk else para
                    current_ids.extend(para_ids)

            if current_chunk.strip():
                chunk_id = f"{document_name}::chunk_{section_idx}_{sub_idx}"
                chunks.append(DocumentChunk(
                    chunk_id=chunk_id,
                    text=current_chunk.strip(),
                    document_name=document_name,
                    source_ids=current_ids,
                ))

    return chunks


def load_documents(source_dir: Optional[str] = None) -> None:
    """
    Load all Markdown source documents, parse citations, and build the index.
    
    This is called once at startup (or lazily on first API request).
    """
    global _citation_index, _document_metadata, _document_chunks, _is_loaded

    if _is_loaded:
        return

    settings = get_settings()
    doc_dir = Path(source_dir or settings.SOURCE_DOCUMENTS_DIR)

    if not doc_dir.exists():
        raise FileNotFoundError(f"Source documents directory not found: {doc_dir}")

    md_files = sorted(doc_dir.glob("*.md"))

    if not md_files:
        raise FileNotFoundError(f"No Markdown files found in: {doc_dir}")

    for md_file in md_files:
        content = md_file.read_text(encoding="utf-8")
        doc_name = md_file.stem  # e.g., "legora_privacy"

        # Parse citations
        citations = _parse_citations(content, doc_name)
        _citation_index.update(citations)

        # Chunk for vector store
        chunks = _chunk_document(content, doc_name)
        _document_chunks.extend(chunks)

        # Build metadata
        metadata = DocumentMetadata(
            filename=md_file.name,
            title=_extract_title(content),
            total_citations=len(citations),
            sections=_extract_sections(content),
        )
        _document_metadata.append(metadata)

    _is_loaded = True


def get_citation_index() -> dict[str, dict]:
    """Return the full citation index as serializable dicts."""
    _ensure_loaded()
    return {
        sid: {
            "source_id": c.source_id,
            "text": c.text,
            "document_name": c.document_name,
            "section_heading": c.section_heading,
        }
        for sid, c in _citation_index.items()
    }


def get_citation(source_id: str) -> Optional[Citation]:
    """Look up a single citation by its SourceID."""
    _ensure_loaded()
    return _citation_index.get(source_id)


def get_document_metadata() -> list[dict]:
    """Return metadata for all ingested documents."""
    _ensure_loaded()
    return [
        {
            "filename": m.filename,
            "title": m.title,
            "total_citations": m.total_citations,
            "sections": m.sections,
        }
        for m in _document_metadata
    ]


def get_all_chunks() -> list[DocumentChunk]:
    """Return all document chunks (for vector store indexing)."""
    _ensure_loaded()
    return _document_chunks


def _ensure_loaded():
    """Lazy-load documents if not already done."""
    if not _is_loaded:
        load_documents()
