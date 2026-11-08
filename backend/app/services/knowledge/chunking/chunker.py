"""
ACREVIA - KrishiBrain Structure-Aware Document Chunker.
Splits extracted sections into concept-preserving chunks with citation boundaries.
"""

import hashlib
from typing import List, Dict, Any, Optional
from backend.app.services.knowledge.extraction.extractors import ExtractedSection


class ChunkData:
    def __init__(
        self,
        chunk_index: int,
        content: str,
        heading_path: str,
        parent_section: Optional[str] = None,
        page_start: Optional[int] = None,
        page_end: Optional[int] = None,
        token_count: int = 0,
        content_hash: str = ""
    ):
        self.chunk_index = chunk_index
        self.content = content
        self.heading_path = heading_path
        self.parent_section = parent_section
        self.page_start = page_start
        self.page_end = page_end
        self.token_count = token_count
        self.content_hash = content_hash or hashlib.sha256(content.encode("utf-8")).hexdigest()


class StructureAwareChunker:
    def __init__(
        self,
        target_chunk_tokens: int = 250,
        overlap_tokens: int = 40,
        min_chunk_tokens: int = 30
    ):
        self.target_chunk_tokens = target_chunk_tokens
        self.overlap_tokens = overlap_tokens
        self.min_chunk_tokens = min_chunk_tokens

    def chunk_sections(self, sections: List[ExtractedSection]) -> List[ChunkData]:
        chunks: List[ChunkData] = []
        chunk_idx = 0

        for section in sections:
            words = section.text.split()
            if not words:
                continue

            # Estimate ~1.3 tokens per word
            if len(words) <= self.target_chunk_tokens:
                # Section fits in one chunk
                content = section.text
                c_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
                chunks.append(ChunkData(
                    chunk_index=chunk_idx,
                    content=content,
                    heading_path=section.heading_path,
                    parent_section=section.parent_heading or section.heading,
                    page_start=section.page_num,
                    page_end=section.page_num,
                    token_count=int(len(words) * 1.3),
                    content_hash=c_hash
                ))
                chunk_idx += 1
            else:
                # Split with overlap
                step = self.target_chunk_tokens - self.overlap_tokens
                for i in range(0, len(words), step):
                    chunk_words = words[i:i + self.target_chunk_tokens]
                    if len(chunk_words) < self.min_chunk_tokens and i > 0:
                        continue
                    content = " ".join(chunk_words)
                    c_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
                    chunks.append(ChunkData(
                        chunk_index=chunk_idx,
                        content=content,
                        heading_path=section.heading_path,
                        parent_section=section.parent_heading or section.heading,
                        page_start=section.page_num,
                        page_end=section.page_num,
                        token_count=int(len(chunk_words) * 1.3),
                        content_hash=c_hash
                    ))
                    chunk_idx += 1

        return chunks
