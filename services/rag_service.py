"""Retrieval, chunking, source coverage, citation support checking."""
from __future__ import annotations

import hashlib
import html
import math
import re
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple

import numpy as np
from pypdf import PdfReader


@dataclass
class SourceChunk:
    id: str
    chunk_index: int
    text: str
    score: float
    method: str
    doc_name: str
    page: Optional[int] = None
    embedding: Optional[List[float]] = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "chunk_index": self.chunk_index,
            "doc_name": self.doc_name,
            "page": self.page,
            "score": round(float(self.score), 4),
            "method": self.method,
            "text": self.text,
        }


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").replace("\x00", " ")).strip()


def extract_text_from_upload(uploaded_file) -> Tuple[str, str]:
    """Extract text from PDF/TXT/MD upload."""
    if uploaded_file is None:
        return "", ""
    name = getattr(uploaded_file, "name", "uploaded_file")
    suffix = name.lower().split(".")[-1]
    if suffix == "pdf":
        reader = PdfReader(uploaded_file)
        parts = []
        for i, page in enumerate(reader.pages, start=1):
            try:
                txt = page.extract_text() or ""
            except Exception:
                txt = ""
            if txt.strip():
                parts.append(f"[Page {i}] {txt}")
        return clean_text("\n".join(parts)), name
    raw = uploaded_file.read()
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8", errors="ignore")
    return clean_text(str(raw)), name


def chunk_text(text: str, doc_name: str = "document", chunk_size: int = 1200, overlap: int = 180) -> List[SourceChunk]:
    text = clean_text(text)
    chunks: List[SourceChunk] = []
    if not text:
        return chunks
    start = 0
    idx = 1
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(SourceChunk(id=f"S{idx}", chunk_index=idx, text=chunk, score=0.0, method="initial", doc_name=doc_name))
            idx += 1
        if end == len(text):
            break
        start = max(0, end - overlap)
    return chunks


def local_hash_embedding(text: str, dims: int = 96) -> List[float]:
    """Deterministic toy embedding for Demo Mode."""
    tokens = re.findall(r"[a-zA-Z0-9_]{3,}", text.lower())
    vec = np.zeros(dims, dtype=float)
    for token in tokens:
        h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
        vec[h % dims] += 1.0
    norm = np.linalg.norm(vec)
    if norm:
        vec = vec / norm
    return vec.tolist()


def cosine_similarity(a: Iterable[float], b: Iterable[float]) -> float:
    va = np.array(list(a), dtype=float)
    vb = np.array(list(b), dtype=float)
    denom = np.linalg.norm(va) * np.linalg.norm(vb)
    if denom == 0:
        return 0.0
    return float(np.dot(va, vb) / denom)


def keyword_score(query: str, text: str) -> float:
    q_terms = set(re.findall(r"[a-zA-Z0-9_]{4,}", query.lower()))
    if not q_terms:
        return 0.0
    t = text.lower()
    hits = sum(1 for term in q_terms if term in t)
    return hits / max(1, len(q_terms))


def rank_chunks(query: str, chunks: List[SourceChunk], embeddings: Optional[List[List[float]]] = None, query_embedding: Optional[List[float]] = None, top_k: int = 8) -> List[SourceChunk]:
    ranked: List[SourceChunk] = []
    for i, chunk in enumerate(chunks):
        semantic = 0.0
        if embeddings and query_embedding and i < len(embeddings):
            semantic = cosine_similarity(query_embedding, embeddings[i])
            chunk.embedding = embeddings[i]
        lexical = keyword_score(query, chunk.text)
        score = 0.72 * semantic + 0.28 * lexical if semantic else lexical
        ranked.append(SourceChunk(
            id=chunk.id,
            chunk_index=chunk.chunk_index,
            text=chunk.text,
            score=score,
            method="embedding+keyword" if semantic else "keyword",
            doc_name=chunk.doc_name,
            page=chunk.page,
            embedding=chunk.embedding,
        ))
    ranked.sort(key=lambda c: c.score, reverse=True)
    # Reassign display IDs by rank so citations are compact and verifiable
    top = ranked[:top_k]
    return [SourceChunk(id=f"S{i+1}", chunk_index=c.chunk_index, text=c.text, score=c.score, method=c.method, doc_name=c.doc_name, page=c.page, embedding=c.embedding) for i, c in enumerate(top)]


def highlight_terms(text: str, query: str) -> str:
    safe = html.escape(text)
    terms = sorted(set(re.findall(r"[a-zA-Z0-9_]{5,}", query.lower())), key=len, reverse=True)[:12]
    for term in terms:
        safe = re.sub(f"({re.escape(term)})", r"<mark>\1</mark>", safe, flags=re.IGNORECASE)
    return safe


def find_citations(markdown: str) -> List[str]:
    return sorted(set(re.findall(r"\[(S\d+)\]", markdown or "")), key=lambda s: int(s[1:]))


def verify_citations(markdown: str, sources: List[SourceChunk]) -> List[Dict[str, Any]]:
    source_ids = {s.id: s for s in sources}
    citations = find_citations(markdown)
    rows = []
    for cid in citations:
        src = source_ids.get(cid)
        rows.append({
            "citation": cid,
            "exists": bool(src),
            "source_score": round(src.score, 4) if src else None,
            "doc_name": src.doc_name if src else None,
            "verification": "Verified source id" if src else "Missing source id",
            "quote_preview": (src.text[:240] + "...") if src and len(src.text) > 240 else (src.text if src else ""),
        })
    return rows


def source_coverage(all_chunks: List[SourceChunk], used_sources: List[SourceChunk]) -> Dict[str, Any]:
    used_indices = {s.chunk_index for s in used_sources}
    return {
        "total_chunks": len(all_chunks),
        "used_chunks": len(used_sources),
        "unused_chunks": max(0, len(all_chunks) - len(used_sources)),
        "coverage_ratio": round(len(used_sources) / max(1, len(all_chunks)), 3),
        "used_source_ids": [s.id for s in used_sources],
        "not_used_chunk_indexes": [c.chunk_index for c in all_chunks if c.chunk_index not in used_indices][:30],
        "limitations": "PDF extraction may miss scanned images, tables, charts, signatures, and low-quality OCR content.",
    }


def build_source_context(sources: List[SourceChunk]) -> str:
    return "\n\n".join([f"[{s.id}] {s.text}" for s in sources])
