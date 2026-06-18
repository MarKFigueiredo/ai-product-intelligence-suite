"""Citation support, quote grounding, and Interpret-specific validation utilities.

The functions in this module are deliberately rule-based and conservative.
They do not prove legal correctness. Their purpose is to make grounding quality
visible before human review by checking whether generated claims are supported
by the cited source text.
"""
from __future__ import annotations

import difflib
import re
from typing import Any, Dict, Iterable, List, Optional, Tuple

from services.rag_service import SourceChunk

STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "into", "must", "should", "shall", "will",
    "are", "was", "were", "have", "has", "been", "before", "after", "where", "when", "which", "their",
    "there", "under", "over", "between", "through", "about", "using", "used", "use", "user", "users",
    "system", "product", "document", "requirement", "requirements", "rule", "rules", "data", "field",
    "include", "includes", "included", "record", "records", "information", "software", "application",
}

OBLIGATION_TERMS = {
    "must", "shall", "required", "require", "requires", "mandatory", "need", "needs", "before", "after",
    "validate", "validation", "block", "prevent", "submit", "export", "report", "retain", "evidence",
    "correct", "correction", "review", "audit", "exception", "deadline", "submission",
}

NEGATION_TERMS = {"not", "never", "no", "without", "except", "unless", "optional", "recommended", "may"}


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def tokenize(text: str, *, keep_stopwords: bool = False) -> List[str]:
    tokens = re.findall(r"[a-zA-Z0-9_]{2,}", normalize_text(text))
    if keep_stopwords:
        return tokens
    return [t for t in tokens if t not in STOPWORDS and len(t) >= 3]


def split_sentences(text: str) -> List[str]:
    raw = re.split(r"(?<=[.!?;:])\s+|\n+|(?<=\])\s+", text or "")
    sentences = [s.strip() for s in raw if len(s.strip()) > 18]
    if sentences:
        return sentences
    return [text[:700].strip()] if text else []


def jaccard_score(a: Iterable[str], b: Iterable[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def containment_score(claim_tokens: Iterable[str], source_tokens: Iterable[str]) -> float:
    claim_set, source_set = set(claim_tokens), set(source_tokens)
    if not claim_set:
        return 0.0
    return len(claim_set & source_set) / len(claim_set)


def char_ngram_score(a: str, b: str, n: int = 4) -> float:
    def grams(text: str) -> set[str]:
        t = re.sub(r"\s+", " ", normalize_text(text))
        if len(t) <= n:
            return {t} if t else set()
        return {t[i:i+n] for i in range(len(t)-n+1)}
    ga, gb = grams(a), grams(b)
    if not ga or not gb:
        return 0.0
    return len(ga & gb) / len(ga | gb)


def numbers_in(text: str) -> List[str]:
    return re.findall(r"\b\d+(?:[.,]\d+)?%?\b", text or "")


def modal_terms(text: str) -> set[str]:
    toks = set(tokenize(text, keep_stopwords=True))
    return toks & OBLIGATION_TERMS


def negation_terms(text: str) -> set[str]:
    toks = set(tokenize(text, keep_stopwords=True))
    return toks & NEGATION_TERMS


def citation_ids(text: str) -> List[str]:
    return sorted(set(re.findall(r"\[(S\d+)\]", text or "")), key=lambda x: int(x[1:]))


def source_map(sources: List[SourceChunk]) -> Dict[str, SourceChunk]:
    return {s.id: s for s in sources}


def fuzzy_quote_present(quote: str, source_text: str) -> Tuple[bool, int]:
    """Return whether a proposed quote is actually present or nearly present.

    The second value is a 0-100 quote integrity score.
    """
    q = normalize_text(quote)
    s = normalize_text(source_text)
    if not q:
        return False, 0
    if q in s:
        return True, 100
    q_tokens = tokenize(q)
    s_tokens = tokenize(s)
    containment = containment_score(q_tokens, s_tokens)
    ngram = char_ngram_score(q, s)
    seq = difflib.SequenceMatcher(None, q[:500], s[:2500]).ratio()
    score = round((0.58 * containment + 0.27 * ngram + 0.15 * seq) * 100)
    return score >= 78, max(0, min(100, score))


def support_components(claim: str, source_text: str) -> Dict[str, Any]:
    claim_tokens = tokenize(claim)
    source_tokens = tokenize(source_text)
    containment = containment_score(claim_tokens, source_tokens)
    jaccard = jaccard_score(claim_tokens, source_tokens)
    ngram = char_ngram_score(claim, source_text)
    seq_ratio = difflib.SequenceMatcher(None, normalize_text(claim)[:800], normalize_text(source_text)[:2500]).ratio()

    claim_numbers = set(numbers_in(claim))
    source_numbers = set(numbers_in(source_text))
    missing_numbers = sorted(claim_numbers - source_numbers)
    number_penalty = 0.18 if missing_numbers else 0.0

    claim_modals = modal_terms(claim)
    source_modals = modal_terms(source_text)
    modal_alignment = len(claim_modals & source_modals) / max(1, len(claim_modals)) if claim_modals else 0.5

    claim_negs = negation_terms(claim)
    source_negs = negation_terms(source_text)
    negation_mismatch = bool((claim_negs and not source_negs) or (source_negs and not claim_negs and claim_modals))
    negation_penalty = 0.12 if negation_mismatch else 0.0

    exact_boost = 0.10 if normalize_text(claim)[:90] and normalize_text(claim)[:90] in normalize_text(source_text) else 0.0
    raw = (0.47 * containment) + (0.17 * jaccard) + (0.16 * ngram) + (0.10 * seq_ratio) + (0.10 * modal_alignment) + exact_boost
    raw = max(0.0, raw - number_penalty - negation_penalty)
    score = max(0, min(100, round(raw * 100)))
    return {
        "support_score": score,
        "token_containment": round(containment, 3),
        "jaccard": round(jaccard, 3),
        "char_ngram": round(ngram, 3),
        "sequence_ratio": round(seq_ratio, 3),
        "modal_alignment": round(modal_alignment, 3),
        "missing_numbers": missing_numbers,
        "negation_mismatch": negation_mismatch,
        "claim_terms": sorted(set(claim_tokens))[:40],
        "source_terms_matched": sorted(set(claim_tokens) & set(source_tokens))[:40],
    }


def support_score(claim: str, source_text: str) -> int:
    return int(support_components(claim, source_text)["support_score"])


def best_supporting_quote(claim: str, source_text: str, proposed_quote: str = "", max_len: int = 360) -> Tuple[str, int, Dict[str, Any]]:
    """Find the strongest sentence-level quote for a claim.

    If a model-proposed quote is present in the source, prefer it. Otherwise,
    select the best sentence from the cited source chunk.
    """
    if proposed_quote:
        quote_present, quote_score = fuzzy_quote_present(proposed_quote, source_text)
        if quote_present:
            quote = proposed_quote.strip()
            if len(quote) > max_len:
                quote = quote[:max_len].rstrip() + "..."
            comps = support_components(claim, quote)
            comps["quote_integrity_score"] = quote_score
            comps["quote_source"] = "model_proposed_quote_present_in_source"
            return quote, max(int(comps["support_score"]), quote_score), comps

    best_sentence = ""
    best_score = -1
    best_components: Dict[str, Any] = {}
    for sentence in split_sentences(source_text):
        comps = support_components(claim, sentence)
        score = int(comps["support_score"])
        if score > best_score:
            best_score = score
            best_sentence = sentence
            best_components = comps
    if not best_sentence:
        best_sentence = source_text[:max_len]
        best_components = support_components(claim, best_sentence)
        best_score = int(best_components["support_score"])
    if len(best_sentence) > max_len:
        best_sentence = best_sentence[:max_len].rstrip() + "..."
    best_components["quote_integrity_score"] = 0
    best_components["quote_source"] = "best_sentence_from_cited_source"
    return best_sentence, max(0, best_score), best_components


def status_from_score(score: int, *, missing_source: bool = False, quote_missing: bool = False, negation_mismatch: bool = False) -> str:
    if missing_source:
        return "Missing source id"
    if negation_mismatch:
        return "Needs human review — possible modality/negation mismatch"
    if quote_missing and score < 78:
        return "Needs human review — proposed quote not found"
    if score >= 82:
        return "Strong support"
    if score >= 64:
        return "Partial support"
    if score >= 42:
        return "Weak support"
    return "Unsupported / needs review"


def _claim_rows_from_data(data: Dict[str, Any]) -> List[Dict[str, str]]:
    """Pull likely product claims from structured JSON output."""
    claim_rows: List[Dict[str, str]] = []
    sections = [
        ("obligation_extraction", "obligation", "source", "quote_support"),
        ("obligation_extraction", "mandatory_fields", "source", "quote_support"),
        ("traceability_matrix", "obligation", "source", "quote_support"),
        ("traceability_matrix", "validation_rule", "source", "quote_support"),
        ("traceability_matrix", "product_impact", "source", "quote_support"),
        ("product_requirements", "requirement", "source", "quote_support"),
        ("validation_rules", "logic", "source", "quote_support"),
        ("qa_test_cases", "scenario", "source", "quote_support"),
        ("source_quote_candidates", "claim", "citation", "quote_support"),
    ]
    for section, claim_key, citation_key, quote_key in sections:
        rows = data.get(section, [])
        if not isinstance(rows, list):
            continue
        for idx, row in enumerate(rows, start=1):
            if not isinstance(row, dict):
                continue
            claim = str(row.get(claim_key, "")).strip()
            cited = str(row.get(citation_key, "")).strip()
            proposed_quote = str(row.get(quote_key, "") or row.get("quote", "") or row.get("source_quote", "")).strip()
            for citation in citation_ids(cited):
                if claim:
                    claim_rows.append({
                        "section": section,
                        "row": str(idx),
                        "claim_key": claim_key,
                        "claim": claim,
                        "citation": citation,
                        "proposed_quote": proposed_quote,
                    })
    seen = set()
    unique: List[Dict[str, str]] = []
    for row in claim_rows:
        key = (row["section"], row["claim_key"], row["claim"].lower(), row["citation"])
        if key not in seen:
            seen.add(key)
            unique.append(row)
    return unique[:120]


def verify_citations_advanced(data: Dict[str, Any], sources: List[SourceChunk]) -> List[Dict[str, Any]]:
    """Check whether generated claims are supported by cited source chunks.

    This is not legal/compliance validation. It is a product-quality guardrail
    to expose weak grounding before human review.
    """
    smap = source_map(sources)
    rows: List[Dict[str, Any]] = []
    for claim_row in _claim_rows_from_data(data):
        citation = claim_row["citation"]
        source = smap.get(citation)
        proposed_quote = claim_row.get("proposed_quote", "")
        if not source:
            rows.append({
                **claim_row,
                "exists": False,
                "support_score": 0,
                "verification_status": status_from_score(0, missing_source=True),
                "supporting_quote": "",
                "quote_present_in_source": False,
                "quote_integrity_score": 0,
                "review_required": True,
                "review_reason": "The citation ID is not available in the retrieved source set.",
                "source_score": None,
                "verification_method": "rule-based source-id and textual support check",
            })
            continue

        quote_present, quote_integrity = fuzzy_quote_present(proposed_quote, source.text) if proposed_quote else (False, 0)
        quote, quote_score, comps = best_supporting_quote(claim_row["claim"], source.text, proposed_quote)
        whole_comps = support_components(claim_row["claim"], source.text)
        score = max(int(quote_score), int(whole_comps["support_score"]))
        neg_mismatch = bool(comps.get("negation_mismatch") or whole_comps.get("negation_mismatch"))
        quote_missing = bool(proposed_quote and not quote_present)
        status = status_from_score(score, quote_missing=quote_missing, negation_mismatch=neg_mismatch)
        review_required = score < 64 or quote_missing or neg_mismatch or bool(comps.get("missing_numbers"))
        review_reasons: List[str] = []
        if score < 64:
            review_reasons.append("Low textual support score")
        if quote_missing:
            review_reasons.append("Model-proposed quote was not found in the cited source")
        if neg_mismatch:
            review_reasons.append("Potential modality or negation mismatch")
        if comps.get("missing_numbers"):
            review_reasons.append("Claim contains numbers not found in the cited source")
        if not review_reasons:
            review_reasons.append("No immediate issue detected by rule-based checks")

        rows.append({
            **claim_row,
            "exists": True,
            "support_score": score,
            "verification_status": status,
            "supporting_quote": quote,
            "quote_present_in_source": quote_present,
            "quote_integrity_score": quote_integrity,
            "review_required": review_required,
            "review_reason": "; ".join(review_reasons),
            "token_containment": whole_comps.get("token_containment"),
            "jaccard": whole_comps.get("jaccard"),
            "char_ngram": whole_comps.get("char_ngram"),
            "modal_alignment": whole_comps.get("modal_alignment"),
            "matched_terms": ", ".join(whole_comps.get("source_terms_matched", [])[:18]),
            "missing_numbers": ", ".join(whole_comps.get("missing_numbers", [])),
            "source_score": round(float(source.score), 4),
            "source_doc": source.doc_name,
            "source_chunk_index": source.chunk_index,
            "retrieval_method": source.method,
            "source_text_preview": source.text[:320] + ("..." if len(source.text) > 320 else ""),
            "verification_method": "rule-based source-id, quote integrity, lexical/semantic-ish support check",
        })
    return rows


def grounding_summary(citation_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not citation_rows:
        return {
            "verified_claims": 0,
            "average_support_score": 0,
            "weak_or_missing_claims": 0,
            "quote_integrity_rate": 0,
            "human_review_required": True,
        }
    scores = [int(r.get("support_score") or 0) for r in citation_rows]
    weak = [r for r in citation_rows if r.get("review_required") or int(r.get("support_score") or 0) < 64 or not r.get("exists")]
    rows_with_proposed_quotes = [r for r in citation_rows if r.get("proposed_quote")]
    quote_ok = [r for r in rows_with_proposed_quotes if r.get("quote_present_in_source")]
    return {
        "verified_claims": len(citation_rows),
        "average_support_score": round(sum(scores) / max(1, len(scores))),
        "weak_or_missing_claims": len(weak),
        "quote_integrity_rate": round(100 * len(quote_ok) / max(1, len(rows_with_proposed_quotes))) if rows_with_proposed_quotes else 0,
        "human_review_required": bool(weak),
    }


def grounding_heatmap_items(citation_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        {
            "label": f"{r.get('section','claim')} {r.get('row','')}",
            "grounding_score": int(r.get("support_score") or 0),
            "human_review": r.get("verification_status", "Review"),
        }
        for r in citation_rows[:16]
    ]


def build_obligation_support_matrix(data: Dict[str, Any], citation_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create one row per extracted obligation with exact quote-level support."""
    obligations = data.get("obligation_extraction", []) or []
    rows: List[Dict[str, Any]] = []
    for idx, obligation in enumerate(obligations, start=1):
        if not isinstance(obligation, dict):
            continue
        obligation_text = str(obligation.get("obligation", "")).strip()
        source_ids = citation_ids(str(obligation.get("source", "")))
        matching = [r for r in citation_rows if r.get("section") == "obligation_extraction" and r.get("row") == str(idx)]
        best = max(matching, key=lambda r: int(r.get("support_score") or 0), default={})
        rows.append({
            "obligation_id": obligation.get("obligation_id", f"O{idx}"),
            "obligation": obligation_text,
            "source": ", ".join(source_ids) or obligation.get("source", ""),
            "mandatory_fields": obligation.get("mandatory_fields", ""),
            "best_supporting_quote": best.get("supporting_quote", "No quote selected"),
            "support_score": best.get("support_score", 0),
            "support_status": best.get("verification_status", "No support row found"),
            "review_required": bool(best.get("review_required", True)),
            "review_reason": best.get("review_reason", "No rule-based support row found"),
        })
    return rows


def build_human_review_queue(data: Dict[str, Any], citation_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Combine model-suggested review items with rule-based weak-citation items."""
    queue: List[Dict[str, Any]] = []
    for idx, item in enumerate(data.get("human_review_queue", []) or [], start=1):
        if isinstance(item, dict):
            queue.append({
                "review_id": f"M{idx}",
                "source": "model-suggested",
                "item": item.get("item", ""),
                "reason": item.get("reason", ""),
                "reviewer": item.get("reviewer", "Compliance/Product"),
                "priority": item.get("priority", "Medium"),
                "status": "Open",
            })
    weak_rows = [r for r in citation_rows if r.get("review_required")]
    for idx, row in enumerate(weak_rows[:40], start=1):
        queue.append({
            "review_id": f"R{idx}",
            "source": "rule-based citation support check",
            "item": row.get("claim", ""),
            "reason": row.get("review_reason", row.get("verification_status", "Needs review")),
            "citation": row.get("citation", ""),
            "support_score": row.get("support_score", 0),
            "reviewer": "Compliance/Product",
            "priority": "High" if int(row.get("support_score") or 0) < 42 else "Medium",
            "status": "Open",
        })
    # de-duplicate by item+reason
    seen = set()
    unique = []
    for row in queue:
        key = (str(row.get("item", "")).lower(), str(row.get("reason", "")).lower())
        if key not in seen:
            seen.add(key)
            unique.append(row)
    return unique


def claim_similarity(a: str, b: str) -> int:
    comps = support_components(a, b)
    return int(comps["support_score"])


def obligation_sentences(text: str) -> List[str]:
    sentences = split_sentences(text)
    rows = []
    for s in sentences:
        toks = set(tokenize(s, keep_stopwords=True))
        if toks & OBLIGATION_TERMS or any(term in normalize_text(s) for term in ["required", "mandatory", "before export", "must include", "shall"]):
            rows.append(s)
    return rows[:120]


def rule_based_version_diff(previous_text: str, current_text: str) -> List[Dict[str, Any]]:
    """Create a conservative diff of obligation-like sentences between two versions."""
    previous = obligation_sentences(previous_text)
    current = obligation_sentences(current_text)
    rows: List[Dict[str, Any]] = []
    matched_previous: set[int] = set()

    for c_idx, current_sentence in enumerate(current, start=1):
        scored = [(p_idx, claim_similarity(current_sentence, prev_sentence)) for p_idx, prev_sentence in enumerate(previous, start=1)]
        best_idx, best_score = max(scored, key=lambda x: x[1], default=(None, 0))
        if best_idx is None or best_score < 42:
            rows.append({
                "change_type": "Added",
                "current_item": current_sentence,
                "previous_item": "",
                "similarity": best_score,
                "product_impact_hint": "Assess whether a new validation rule, requirement or QA case is required.",
                "review_required": True,
            })
        elif best_score < 82:
            matched_previous.add(best_idx)
            rows.append({
                "change_type": "Changed",
                "current_item": current_sentence,
                "previous_item": previous[best_idx - 1],
                "similarity": best_score,
                "product_impact_hint": "Review requirement wording, validation severity and release communication impact.",
                "review_required": True,
            })
        else:
            matched_previous.add(best_idx)
            rows.append({
                "change_type": "Unchanged / similar",
                "current_item": current_sentence,
                "previous_item": previous[best_idx - 1],
                "similarity": best_score,
                "product_impact_hint": "No material change detected by rule-based comparison.",
                "review_required": False,
            })

    for p_idx, previous_sentence in enumerate(previous, start=1):
        if p_idx not in matched_previous:
            rows.append({
                "change_type": "Removed",
                "current_item": "",
                "previous_item": previous_sentence,
                "similarity": 0,
                "product_impact_hint": "Check whether an existing requirement, validation rule or release note should be removed or downgraded.",
                "review_required": True,
            })
    return rows


def highlight_claim_terms(text: str, claim: str) -> str:
    """Return HTML with claim terms highlighted for source inspection."""
    import html

    safe = html.escape(text or "")
    terms = sorted(set(tokenize(claim)), key=len, reverse=True)[:18]
    for term in terms:
        safe = re.sub(f"({re.escape(term)})", r"<mark>\1</mark>", safe, flags=re.IGNORECASE)
    return safe
