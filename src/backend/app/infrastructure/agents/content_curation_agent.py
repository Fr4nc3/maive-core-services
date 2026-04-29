"""
Content Curation Agent.

Queries the RAG knowledge base for relevant NASA content and uses the LLM
to craft a context-appropriate help response for the user.

Pillar: Configuration Layer
Phase: R
Purpose: Multi-agent layer; system prompts and decision logic.
Documented in: docs/paper/maive-systems-engineering-extended.md
"""

import json
import logging
from pathlib import Path

from app.domain.interfaces.knowledge_document_repository import (
    KnowledgeDocumentRepository,
)
from app.infrastructure.ai.embedding_service import EmbeddingService
from app.infrastructure.ai.llm_provider import ChatMessage, LLMProvider

logger = logging.getLogger(__name__)

_PROMPT_PATH = Path(__file__).parent / "prompts" / "content_curation.txt"


class ContentCurationAgent:
    def __init__(
        self,
        llm: LLMProvider,
        knowledge_repo: KnowledgeDocumentRepository,
        embedding_service: EmbeddingService,
    ) -> None:
        self._llm = llm
        self._knowledge_repo = knowledge_repo
        self._embedding_service = embedding_service
        self._system_prompt = _PROMPT_PATH.read_text(encoding="utf-8")

    async def curate(
        self,
        learner_profile: dict,
        query: str,
        help_type: str = "explanation",
    ) -> dict:
        # Build search query from learner context + explicit query
        planet = learner_profile.get("current_planet", "")
        search_text = f"{planet} {query}" if planet else query

        query_embedding = await self._embedding_service.embed(search_text)

        docs = await self._knowledge_repo.vector_search(
            embedding=query_embedding,
            body_id=planet.lower() if planet else None,
            limit=5,
        )

        rag_context = [
            {
                "title": d.title,
                "body_name": d.body_name,
                "content_text": d.content_text,
                "section_tags": d.section_tags,
            }
            for d in docs
        ]

        user_msg = json.dumps(
            {
                "learner_profile": {
                    "engagement_level": learner_profile.get("engagement_level", "medium"),
                    "knowledge_gaps": learner_profile.get("knowledge_gaps", []),
                    "current_planet": planet,
                    "current_section": learner_profile.get("current_section", ""),
                    "difficulty_fit": learner_profile.get("difficulty_fit", "appropriate"),
                },
                "query": query,
                "rag_context": rag_context,
                "help_type": help_type,
            },
            default=str,
        )

        response = await self._llm.chat(
            messages=[
                ChatMessage(role="system", content=self._system_prompt),
                ChatMessage(role="user", content=user_msg),
            ],
            temperature=0.4,
            max_tokens=512,
        )

        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            logger.warning("Content Curation Agent returned non-JSON: %s", response.content)
            return {
                "response_text": response.content[:300],
                "source_title": docs[0].title if docs else "",
                "source_body": docs[0].body_name if docs else "",
                "difficulty_adjusted": False,
                "follow_up_question": "",
                "reasoning": "Fallback — raw LLM output used.",
            }
