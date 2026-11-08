"""
ACREVIA - KrishiBrain Grounded Answer Generator & Safety Guard.
Enforces evidence grounding, CIBRC chemical advice safeguards, and explicit abstention.
"""

import uuid
import time
from typing import List, Dict, Any, Optional
from backend.app.schemas.knowledge import (
    KnowledgeQueryRequest,
    KnowledgeQueryResponse,
    CitationResponse,
)
from backend.app.services.knowledge.retrieval.retriever import ScoredChunk


class AgriculturalSafetyGuard:
    HIGH_RISK_TERMS = [
        "pesticide dose", "chemical spray mixture", "herbicide overdose",
        "insecticide concentration", "tank mix", "banned pesticide",
        "పురుగుమందు మోతాదు", "మందుల మిశ్రమం", "कीटनाशक खुराक"
    ]

    INJECTION_PATTERNS = [
        "ignore previous instructions", "system prompt", "you are now",
        "forget all rules", "bypass safety", "jailbreak"
    ]

    @classmethod
    def sanitize_input(cls, text: str) -> str:
        cleaned = text
        for pat in cls.INJECTION_PATTERNS:
            if pat in cleaned.lower():
                cleaned = cleaned.replace(pat, "[FILTERED]")
        return cleaned

    @classmethod
    def is_high_risk_advice(cls, question: str) -> bool:
        q_lower = question.lower()
        return any(term in q_lower for term in cls.HIGH_RISK_TERMS)


class KnowledgeGenerator:
    @classmethod
    def generate_response(
        cls,
        req: KnowledgeQueryRequest,
        chunks: List[ScoredChunk],
        start_time: float
    ) -> KnowledgeQueryResponse:
        sanitized_q = AgriculturalSafetyGuard.sanitize_input(req.question)
        is_high_risk = AgriculturalSafetyGuard.is_high_risk_advice(sanitized_q)
        query_id = str(uuid.uuid4())

        # 1. Abstention Gate: No relevant chunks found or low score
        if not chunks or chunks[0].score < 0.20:
            return cls._build_abstention_response(req, query_id, start_time, is_high_risk=is_high_risk)

        # 2. Build Citations
        citations: List[CitationResponse] = []
        for scored in chunks:
            c = scored.chunk
            snippet = c.content[:300] + ("..." if len(c.content) > 300 else "")
            citations.append(CitationResponse(
                source_title=scored.document_title,
                publisher=scored.publisher,
                canonical_url=scored.canonical_url,
                document_version=scored.document_version,
                page_start=c.page_start,
                page_end=c.page_end,
                heading_path=c.heading_path,
                content_snippet=snippet,
                relevance_score=round(scored.score, 3)
            ))

        # 3. Determine Evidence Strength & Decision State
        top_score = chunks[0].score
        if top_score >= 0.70:
            evidence_strength = "STRONG"
            answer_status = "ANSWERED"
        elif top_score >= 0.40:
            evidence_strength = "MODERATE"
            answer_status = "ANSWERED"
        else:
            evidence_strength = "WEAK"
            answer_status = "PARTIALLY_ANSWERED"

        if is_high_risk:
            answer_status = "REQUIRES_EXPERT_REVIEW"

        # 4. Synthesize Grounded Answer
        primary_chunk = chunks[0].chunk
        doc_title = chunks[0].document_title
        publisher = chunks[0].publisher

        if req.language == "te":
            answer_text = (
                f"అధికారిక ఆధారాలు ({publisher} - {doc_title}):\n\n"
                f"{primary_chunk.content}\n\n"
                f"గమనిక: క్రిమిసంహారక మరియు ఎరువుల వాడకంలో CIBRC లేబుల్ మార్గదర్శకాలను పాటించండి."
            )
            limitations = ["క్షేత్రస్థాయి పంట దశ మరియు వాతావరణ పరిస్థితులపై ఆధారపడి ఫలితాలు మారవచ్చు."]
            follow_ups = ["పంట ప్రస్తుత దశ ఏమిటి?", "పొలంలో నీటి పారుదల సౌకర్యం ఉందా?"]
        elif req.language == "hi":
            answer_text = (
                f"आधिकारिक कृषि साक्ष्य ({publisher} - {doc_title}):\n\n"
                f"{primary_chunk.content}\n\n"
                f"सलाह: कीटनाशकों और उर्वरकों के उपयोग में हमेशा CIBRC द्वारा अनुमोदित उत्पाद लेबल का पालन करें।"
            )
            limitations = ["खेत के स्थानीय मौसम और फसल की स्थिति के अनुसार प्रभाव भिन्न हो सकता है।"]
            follow_ups = ["आपकी फसल वर्तमान में किस विकास चरण में है?", "क्या खेत में जल निकासी की उचित व्यवस्था है?"]
        else:
            answer_text = (
                f"According to verified agricultural evidence from {publisher} ({doc_title}):\n\n"
                f"{primary_chunk.content}\n\n"
                f"Advisory: Strictly follow CIBRC registered product label instructions and Pre-Harvest Intervals (PHI)."
            )
            limitations = ["Field efficacy depends on local ambient soil moisture, temperature, and crop stage."]
            follow_ups = ["What is the specific vegetative/reproductive stage of the crop?", "Are symptoms uniform across the plot?"]

        if is_high_risk:
            limitations.append("High-risk chemical query flagged: Verified agricultural expert consultation strongly recommended before application.")

        duration_ms = (time.perf_counter() - start_time) * 1000

        return KnowledgeQueryResponse(
            query_id=query_id,
            answer_status=answer_status,
            language=req.language,
            answer=answer_text,
            evidence_strength=evidence_strength,
            citations=citations,
            limitations=limitations,
            follow_up_questions=follow_ups,
            requires_expert_review=is_high_risk or (evidence_strength == "WEAK"),
            execution_time_ms=round(duration_ms, 2)
        )

    @classmethod
    async def generate_response_async(
        cls,
        req: KnowledgeQueryRequest,
        chunks: List[ScoredChunk],
        start_time: float,
        use_groq: bool = True
    ) -> KnowledgeQueryResponse:
        """
        Asynchronously synthesizes grounded responses.
        If GroqCloud is configured and available, generates conversational multilingual guidance
        strictly bounded by retrieved source evidence, with seamless fallback on rate limits or timeout.
        """
        base_resp = cls.generate_response(req, chunks, start_time)

        # Only enhance if base response was successful and not an abstention
        if not use_groq or base_resp.answer_status not in ["ANSWERED", "PARTIALLY_ANSWERED"]:
            return base_resp

        from backend.app.integrations.groq_client import groq_client
        if not groq_client.is_configured:
            return base_resp

        primary_chunk = chunks[0].chunk
        doc_title = chunks[0].document_title
        publisher = chunks[0].publisher

        system_prompt = (
            "You are KrishiBrain, an agricultural AI assistant for farmers in Telangana, India. "
            "You must synthesize an accurate, concise answer based ONLY on the verified evidence below. "
            "Do NOT invent unverified recommendations. Do NOT recommend banned or off-label pesticides. "
            f"Respond in language code: {req.language}."
        )
        user_content = (
            f"Farmer Question: {req.question}\n\n"
            f"Verified Evidence from {publisher} ({doc_title}):\n{primary_chunk.content}"
        )

        groq_res = await groq_client.generate_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.2,
            max_tokens=350
        )

        if groq_res.get("success") and groq_res.get("content"):
            enhanced_answer = (
                f"{groq_res['content'].strip()}\n\n"
                f"---\n"
                f"Source: {publisher} — {doc_title}\n"
                f"Note: Adhere strictly to CIBRC label directions for any chemical application."
            )
            base_resp.answer = enhanced_answer

        return base_resp

    @classmethod
    def _build_abstention_response(
        cls,
        req: KnowledgeQueryRequest,
        query_id: str,
        start_time: float,
        is_high_risk: bool = False
    ) -> KnowledgeQueryResponse:
        duration_ms = (time.perf_counter() - start_time) * 1000

        if is_high_risk:
            status = "REQUIRES_EXPERT_REVIEW"
            if req.language == "te":
                msg = "రక్షణ హెచ్చరిక: అధిక మోతాదు లేదా అనధికార రసాయనాల వాడకం ప్రమాదకరం. CIBRC నిబంధనల ప్రకారం ధృవీకరించబడిన వ్యవసాయ నిపుణుల సలహా తప్పనిసరి."
            elif req.language == "hi":
                msg = "सुरक्षा चेतावनी: अत्यधिक या अनधिकृत रासायनिक कीटनाशक का उपयोग जोखिम भरा है। CIBRC नियमों के तहत प्रमाणित कृषि विशेषज्ञ का परामर्श अनिवार्य है।"
            else:
                msg = "ACREVIA Safety Guard: Requests for non-standard, unverified or extreme chemical pesticide dosages require human expert review under CIBRC safety guidelines. Please consult an agronomist."
            limitations = ["Chemical safety protocol violation suspected. Automated dispensation blocked."]
        else:
            status = "INSUFFICIENT_EVIDENCE"
            if req.language == "te":
                msg = "ఈ ప్రశ్నకు సంబంధించి ధృవీకరించబడిన అధికారిక సమాచారం ప్రస్తుతం లభ్యం కాలేదు. దయచేసి స్థానిక కృషి విజ్ఞాన కేంద్రం (KVK) లేదా వ్యవసాయ నిపుణులను సంప్రదించండి."
            elif req.language == "hi":
                msg = "इस प्रश्न के लिए सत्यापित कृषि प्रमाण वर्तमान में उपलब्ध नहीं है। कृपया नजदीकी कृषि विज्ञान केंद्र (KVK) या कृषि विशेषज्ञ से संपर्क करें।"
            else:
                msg = "Sufficient evidence-backed agricultural documentation is not available in the verified registry for this question. Please consult your local Krishi Vigyan Kendra (KVK) agronomist."
            limitations = ["No approved source in the knowledge registry satisfies the query constraints."]

        return KnowledgeQueryResponse(
            query_id=query_id,
            answer_status=status,
            language=req.language,
            answer=msg,
            evidence_strength="INSUFFICIENT",
            citations=[],
            limitations=limitations,
            follow_up_questions=["Would you like to request an expert review via ExpertConnect?"],
            requires_expert_review=True,
            execution_time_ms=round(duration_ms, 2)
        )
