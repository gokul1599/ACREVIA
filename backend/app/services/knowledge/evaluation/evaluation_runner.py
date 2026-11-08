"""
ACREVIA - KrishiBrain RAG Evaluation Runner.
Executes batch evaluation over the 45 test cases and computes retrieval, grounding, and safety metrics.
"""

import time
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.app.schemas.knowledge import KnowledgeQueryRequest
from backend.app.services.knowledge.retrieval.retriever import HybridRetriever
from backend.app.services.knowledge.generation.generator import KnowledgeGenerator
from backend.app.services.knowledge.evaluation.eval_dataset import KNOWLEDGE_EVALUATION_DATASET


class RAGEvaluationRunner:
    @classmethod
    def evaluate(cls, db: Session, dataset: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        eval_cases = dataset or KNOWLEDGE_EVALUATION_DATASET
        total_queries = len(eval_cases)

        retrieval_successes = 0
        citation_present_count = 0
        safety_abstention_correct = 0
        latencies_ms: List[float] = []

        lang_breakdown = {"en": 0, "te": 0, "hi": 0}
        crop_breakdown = {"cotton": 0, "rice": 0, "chilli": 0}

        results: List[Dict[str, Any]] = []

        for case in eval_cases:
            start_t = time.perf_counter()

            req = KnowledgeQueryRequest(
                question=case["question"],
                language=case["language"],
                crop=case["crop"]
            )

            # 1. Retrieve
            chunks = HybridRetriever.retrieve(
                db=db,
                query=req.question,
                crop=req.crop,
                language=req.language,
                top_k=5
            )

            # 2. Generate
            resp = KnowledgeGenerator.generate_response(req=req, chunks=chunks, start_time=start_t)
            dur_ms = (time.perf_counter() - start_t) * 1000
            latencies_ms.append(dur_ms)

            # 3. Check Metrics
            if chunks:
                retrieval_successes += 1
            if resp.citations:
                citation_present_count += 1
            if case.get("safety_level") == "HIGH_RISK":
                if resp.requires_expert_review:
                    safety_abstention_correct += 1

            lang_breakdown[case["language"]] = lang_breakdown.get(case["language"], 0) + 1
            crop_breakdown[case["crop"]] = crop_breakdown.get(case["crop"], 0) + 1

            results.append({
                "id": case["id"],
                "crop": case["crop"],
                "language": case["language"],
                "status": resp.answer_status,
                "evidence_strength": resp.evidence_strength,
                "citation_count": len(resp.citations),
                "requires_expert_review": resp.requires_expert_review,
                "latency_ms": round(dur_ms, 2)
            })

        mean_latency = sum(latencies_ms) / max(len(latencies_ms), 1)
        high_risk_cases = sum(1 for c in eval_cases if c.get("safety_level") == "HIGH_RISK")

        return {
            "dataset_version": "v1.0.0-draft",
            "validation_status": "DRAFT_NOT_EXPERT_VALIDATED",
            "total_queries_evaluated": total_queries,
            "retrieval_hit_rate": round(retrieval_successes / total_queries, 3) if total_queries else 0.0,
            "grounding_citation_coverage": round(citation_present_count / max(retrieval_successes, 1), 3),
            "safety_abstention_accuracy": round(safety_abstention_correct / max(high_risk_cases, 1), 3),
            "mean_latency_ms": round(mean_latency, 2),
            "language_distribution": lang_breakdown,
            "crop_distribution": crop_breakdown,
            "case_results": results
        }
