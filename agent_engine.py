import re
import os
import json
from typing import Dict, Any, List, Tuple, Optional

from knowledge_base import KnowledgeBase
from memory_manager import ConversationMemory
from handover_manager import HandoverManager

class EduTrustAgentEngine:
    """
    Core AI Orchestrator for EduTrust AI.
    Implements guardrails, RAG prompt engineering, confidence estimation,
    uncertainty handling, and seamless human handover triggering.
    """
    def __init__(self, data_dir: str = "/working_dir/c_608c0f17e2e78757/edutrust_ai/data"):
        self.kb = KnowledgeBase(data_dir=data_dir)
        self.sessions: Dict[str, ConversationMemory] = {}
        self.handover_mgr = HandoverManager()

    def get_or_create_session(self, session_id: str) -> ConversationMemory:
        """Retrieves or creates a ConversationMemory session."""
        if session_id not in self.sessions:
            self.sessions[session_id] = ConversationMemory(session_id=session_id)
        return self.sessions[session_id]

    # --- GUARDRAIL CHECKS ---
    def check_guardrails(self, query: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Runs safety and responsible AI guardrails on user query.
        Returns: (is_flagged: bool, category: str, response_text: str)
        """
        text_lower = query.lower()

        # 1. Self-Harm / Crisis
        crisis_terms = ["suicide", "kill myself", "end my life", "want to die", "self harm", "depressed and hopeless"]
        if any(term in text_lower for term in crisis_terms):
            response = (
                "💙 **Student Well-being Notice**: If you are feeling overwhelmed, hopeless, or in distress, "
                "please know that you are not alone and support is immediately available.\n\n"
                "• **EduTrust Health & Counseling Center**: Call **+1-800-EDUTRUST-HEALTH** (Available 24/7)\n"
                "• **National Crisis Hotline**: Call or text **988**\n"
                "• **Location**: Health Center, next to Hostel Block 3\n\n"
                "Would you like me to notify a campus student counselor to reach out to you directly?"
            )
            return True, "Crisis / Self-Harm", response

        # 2. Academic Dishonesty / Cheating
        cheating_patterns = [
            r'\b(write|solve|do|generate|create)\b.*\b(assignment|homework|essay|exam|code|paper|solution|answers)\b',
            r'\bcheat\b.*\b(exam|test|quiz)\b',
            r'\bgive\s+me\s+answers\b'
        ]
        for p in cheating_patterns:
            if re.search(p, text_lower):
                response = (
                    "⚠️ **Academic Integrity Notice**: In accordance with EduTrust Global University Academic "
                    "Integrity Guidelines (Section 4.2), I cannot write assignments, solve exam questions, "
                    "or generate completed coursework code/essays on your behalf.\n\n"
                    "I can, however, explain theoretical concepts, review study topics, or direct you to "
                    "the **University Tutoring & Writing Center** in Hall C."
                )
                return True, "Academic Integrity Violation", response

        # 3. Profanity / Excessive Toxicity
        profanity_terms = ["fuck", "bitch", "bastard", "asshole", "shit"]
        if any(re.search(rf'\b{p}\b', text_lower) for p in profanity_terms):
            response = (
                "⚠️ **Communication Guideline**: Please maintain respectful language when interacting "
                "with EduTrust AI. I am here to help you resolve your academic questions constructively."
            )
            return True, "Profanity / Toxicity", response

        return False, None, None

    # --- CONFIDENCE EVALUATION ---
    def calculate_confidence(self, query: str, retrieved_docs: List[Dict[str, Any]]) -> Tuple[float, str]:
        """
        Calculates overall AI Confidence Score (0.0 to 1.0) and assigns a confidence tier.
        """
        groundedness = self.kb.compute_groundedness(query, retrieved_docs)
        
        # Check top doc similarity score
        top_doc_score = retrieved_docs[0]["score"] if retrieved_docs else 0.0

        # Combine vector score + groundedness
        overall_confidence = round((0.5 * top_doc_score) + (0.5 * groundedness), 3)

        if overall_confidence >= 0.68:
            level = "High"
        elif overall_confidence >= 0.45:
            level = "Moderate"
        else:
            level = "Low"

        return overall_confidence, level

    # --- RESPONSE GENERATION ---
    def generate_grounded_answer(
        self,
        query: str,
        memory: ConversationMemory,
        retrieved_docs: List[Dict[str, Any]],
        confidence_level: str
    ) -> str:
        """
        Generates factual, grounded response using RAG context and session memory.
        Uses intelligent synthesis with source citations.
        """
        if not retrieved_docs or confidence_level == "Low":
            return (
                "I do not have sufficient official documentation in my knowledge base to answer this "
                "specific question with 100% certainty. To prevent providing inaccurate information, "
                "I recommend checking the **Student Portal** or escalating this query to an Academic Advisor."
            )

        top_doc = retrieved_docs[0]
        sources = list(set([f"[{d['source']}]" for d in retrieved_docs if d['score'] >= 0.35]))
        sources_str = " ".join(sources) if sources else "[Official University Catalog]"

        # Incorporate student entity context if available
        student_name = memory.entities.get("student_name")
        salutation = f"Hello {student_name}! " if student_name else ""

        # High confidence response
        if confidence_level == "High":
            answer = f"{salutation}{top_doc['content']}\n\n**Source Citation**: {sources_str}"
            
            # Check for specific contextual recommendations
            if "Attendance" in top_doc["category"] and memory.entities.get("attendance_percentage"):
                att = memory.entities["attendance_percentage"]
                if att < 75:
                    answer += f"\n\n*Note for your profile*: Your stated attendance is **{att}%**, which is below the 75% threshold. You will need to submit a medical condonation request ($50 fee) to avoid debarment."
            
            if "Course Catalog" in top_doc["category"] and memory.entities.get("target_course"):
                crs = memory.entities["target_course"]
                prereq = top_doc.get("prerequisites", "None")
                answer += f"\n\n*Registration Guidance*: Make sure you have completed the prerequisite **{prereq}** before enrolling in **{crs}**."

            return answer

        # Moderate confidence response with explicit uncertainty disclaimer
        else:
            answer = (
                f"{salutation}Based on available academic guidelines:\n\n{top_doc['content']}\n\n"
                f"ℹ️ **Disclaimer**: This information is provided with moderate confidence. "
                f"Please verify exact requirements with your department coordinator.\n\n"
                f"**Source Citation**: {sources_str}"
            )
            return answer

    # --- MAIN PROCESSING PIPELINE ---
    def process_query(self, query: str, session_id: str = "default_session") -> Dict[str, Any]:
        """
        Full end-to-end processing pipeline for EduTrust AI.
        """
        memory = self.get_or_create_session(session_id)
        
        # 1. Guardrail Check
        is_flagged, guard_cat, guard_resp = self.check_guardrails(query)
        if is_flagged:
            memory.add_message("user", query)
            memory.add_message("assistant", guard_resp, metadata={"guardrail_flagged": True, "category": guard_cat})
            return {
                "answer": guard_resp,
                "confidence_score": 1.0,
                "confidence_level": "High (Guardrail)",
                "groundedness_score": 1.0,
                "friction_score": 0.0,
                "retrieved_sources": [],
                "handover_triggered": False,
                "handover_ticket": None,
                "guardrail_flagged": True,
                "guardrail_category": guard_cat,
                "active_topic": memory.current_topic,
                "entities": memory.entities
            }

        # 2. Memory & Entity Update
        memory.add_message("user", query)
        
        # 3. Sentiment & Friction Analysis
        friction_score = self.handover_mgr.analyze_sentiment_and_friction(query)
        is_explicit = self.handover_mgr.is_explicit_escalation_request(query)

        # 4. RAG Retrieval & Confidence Calculation
        retrieved_docs = self.kb.search(query, top_k=3, score_threshold=0.15)
        conf_score, conf_level = self.calculate_confidence(query, retrieved_docs)
        groundedness_score = self.kb.compute_groundedness(query, retrieved_docs)

        # 5. Handover Trigger Evaluation
        should_handover, trigger_cause, priority = self.handover_mgr.evaluate_handover_trigger(
            query=query,
            confidence_score=conf_score,
            friction_score=friction_score,
            is_explicit=is_explicit
        )

        ticket = None
        if should_handover:
            memory.entities["escalation_requested"] = True
            ticket = self.handover_mgr.create_handover_ticket(
                memory=memory,
                trigger_cause=trigger_cause,
                priority=priority
            )

        # 6. Generate Answer
        if should_handover and is_explicit:
            answer = (
                f"🤝 **Human Handover Initiated**: I have created an urgent support ticket "
                f"(**Ticket ID: {ticket['ticket_id']}**) for an Academic Advisor.\n\n"
                f"**Summary of Issue**: {ticket['summary']['user_issue']}\n"
                f"**Recommended Action**: {ticket['summary']['recommended_human_action']}\n\n"
                f"An advisor has been notified in the **Human Support Queue** and will review your conversation history shortly."
            )
        elif should_handover and conf_score < 0.40:
            base_ans = self.generate_grounded_answer(query, memory, retrieved_docs, conf_level)
            answer = (
                f"{base_ans}\n\n"
                f"⚠️ **Low AI Confidence Notice**: Because my knowledge base lacks a high-confidence match for this query, "
                f"I have automatically generated a support ticket (**Ticket ID: {ticket['ticket_id']}**) "
                f"for human review in the **Live Advisor Queue**."
            )
        else:
            answer = self.generate_grounded_answer(query, memory, retrieved_docs, conf_level)

        # Record assistant turn in memory
        sources_list = [d["source"] for d in retrieved_docs]
        memory.add_message("assistant", answer, metadata={
            "confidence_score": conf_score,
            "confidence_level": conf_level,
            "sources": sources_list,
            "handover_triggered": should_handover
        })

        return {
            "answer": answer,
            "confidence_score": conf_score,
            "confidence_level": conf_level,
            "groundedness_score": groundedness_score,
            "friction_score": friction_score,
            "retrieved_sources": sources_list,
            "retrieved_docs_raw": retrieved_docs,
            "handover_triggered": should_handover,
            "handover_ticket": ticket,
            "guardrail_flagged": False,
            "guardrail_category": None,
            "active_topic": memory.current_topic,
            "entities": memory.entities
        }


if __name__ == "__main__":
    engine = EduTrustAgentEngine()
    print("Testing EduTrustAgentEngine Pipeline...\n")
    
    queries = [
        "Hi, my name is Alex, student ID STU2025102. What is the minimum GPA required for graduation?",
        "What are the prerequisites for AI401 course?",
        "I am so angry with this website! Connect me to a real academic advisor right now!",
        "Can you write my programming assignment code for CS101?"
    ]
    
    for q in queries:
        print(f"User Query: {q}")
        res = engine.process_query(q, session_id="test_session")
        print(f"Confidence: {res['confidence_score']} ({res['confidence_level']}) | Friction: {res['friction_score']}")
        print(f"Topic: {res['active_topic']} | Handover: {res['handover_triggered']}")
        print(f"Answer:\n{res['answer'][:150]}...\n" + "="*50)
