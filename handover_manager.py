import re
import time
import uuid
from typing import List, Dict, Any, Tuple, Optional

class HandoverManager:
    """
    Intelligent Human Handover Module for EduTrust AI.
    Detects friction/sentiment, explicit escalation requests, triggers handover,
    and generates concise, structured handover tickets for human academic advisors.
    """
    def __init__(self):
        self.tickets: List[Dict[str, Any]] = []

    def analyze_sentiment_and_friction(self, text: str) -> float:
        """
        Analyzes message for frustration, anger, or friction keywords.
        Returns friction score between 0.0 (neutral/happy) and 1.0 (extremely frustrated).
        """
        text_lower = text.lower()
        
        high_frustration_terms = [
            "ridiculous", "useless", "terrible", "worst", "unhelpful", "waste of time",
            "frustrated", "angry", "annoyed", "stupid", "idiot", "hate this", "horrible",
            "not answering", "wrong answer", "nonsense", "shut up"
        ]
        medium_frustration_terms = [
            "confused", "don't understand", "doesn't help", "still unclear",
            "asked before", "again", "already told you", "why can't you", "hard to find"
        ]

        high_count = sum(1 for term in high_frustration_terms if term in text_lower)
        med_count = sum(1 for term in medium_frustration_terms if term in text_lower)
        
        # ALL CAPS detection (shouting)
        words = text.split()
        caps_words = [w for w in words if w.isupper() and len(w) > 2]
        caps_ratio = len(caps_words) / max(len(words), 1)

        friction_score = (high_count * 0.4) + (med_count * 0.2) + (caps_ratio * 0.3)
        return min(1.0, round(friction_score, 2))

    def is_explicit_escalation_request(self, text: str) -> bool:
        """Checks if the user explicitly requests a human advisor or support person."""
        text_lower = text.lower()
        patterns = [
            r'\b(?:talk|speak|connect|chat)\s+(?:to|with)?\s+(?:a|an)?\s*(?:human|advisor|person|agent|counselor|representative|officer)\b',
            r'\b(?:escalate|escalation|human support|live chat|real person|academic advisor)\b',
            r'\b(?:transfer me|get me a human|call advisor|need human)\b'
        ]
        for p in patterns:
            if re.search(p, text_lower):
                return True
        return False

    def is_complex_policy_query(self, text: str) -> bool:
        """Detects high-impact or complex policy queries requiring human discretion."""
        text_lower = text.lower()
        complex_terms = [
            "appeal", "dismissal", "suspension", "debarred", "expelled", "cheating accusation",
            "grade dispute", "fee waiver", "medical exemption", "special approval", "financial hardship"
        ]
        return any(term in text_lower for term in complex_terms)

    def evaluate_handover_trigger(
        self,
        query: str,
        confidence_score: float,
        friction_score: float,
        is_explicit: bool
    ) -> Tuple[bool, Optional[str], str]:
        """
        Evaluates multi-factor criteria to determine if human handover should be triggered.
        Returns: (should_handover: bool, trigger_cause: str, priority: str)
        """
        if is_explicit:
            return True, "Explicit User Escalation Request", "High"
            
        if self.is_complex_policy_query(query):
            return True, "Complex Policy / Sensitive Dispute Query", "High"

        if friction_score >= 0.60:
            return True, "High Student Frustration / Negative Sentiment", "Urgent" if friction_score > 0.8 else "High"

        if confidence_score < 0.40:
            return True, "Low AI Groundedness Confidence (< 0.40)", "Medium"

        return False, None, "Low"

    def create_handover_ticket(
        self,
        memory: Any, # ConversationMemory instance
        trigger_cause: str,
        priority: str = "Medium"
    ) -> Dict[str, Any]:
        """
        Generates a structured, concise handover ticket with:
        - User Issue
        - Attempted Steps
        - Missing Context
        - Recommended Human Action
        """
        ticket_id = f"TICK-{time.strftime('%Y')}-{uuid.uuid4().hex[:4].upper()}"
        entities = memory.entities
        topic = memory.current_topic
        messages = memory.messages

        # 1. Identify User Issue
        last_user_msgs = [m['content'] for m in messages if m['role'] == 'user']
        primary_issue = last_user_msgs[-1] if last_user_msgs else "Academic Inquiry"

        # 2. Identify Attempted Steps
        attempted_steps = []
        for m in messages:
            if m['role'] == 'user':
                attempted_steps.append(f"Student asked: '{m['content'][:80]}'")
            elif m['role'] == 'assistant':
                attempted_steps.append(f"AI provided RAG guidance on {topic}")
        
        attempted_str = "; ".join(attempted_steps[-4:]) if attempted_steps else "Student initiated conversation with EduTrust AI."

        # 3. Identify Missing Context
        missing_context_items = []
        if not entities.get("student_id"):
            missing_context_items.append("Verified Student ID")
        if topic == "Attendance Policy" and not entities.get("attendance_percentage"):
            missing_context_items.append("Official Attendance Percentage & Medical Certificate")
        if topic == "Tuition & Financials":
            missing_context_items.append("Official Fee Receipt / Bank Transaction Reference")
        if topic == "Grading & Academic Standing" and not entities.get("cgpa"):
            missing_context_items.append("Official Academic Transcript / Current CGPA")
            
        missing_context_str = ", ".join(missing_context_items) if missing_context_items else "Standard student record verification needed."

        # 4. Identify Recommended Human Action
        if "Attendance" in topic:
            rec_action = "Review student attendance log and evaluate eligibility for 65-75% medical condonation waiver."
        elif "Tuition" in topic or "Financial" in topic:
            rec_action = "Check university bursar portal for payment status and advise on installment options or late fee waiver."
        elif "Grading" in topic or "Complex" in trigger_cause:
            rec_action = "Schedule 1-on-1 academic counseling session to review CGPA improvement plan or grade appeal."
        elif "Course" in topic:
            rec_action = "Verify prerequisite compliance in student portal and manually process course add/drop approval."
        else:
            rec_action = "Contact student directly to address specific inquiry and update academic record."

        structured_summary = {
            "user_issue": f"[{topic}] {primary_issue}",
            "attempted_steps": attempted_str,
            "missing_context": missing_context_str,
            "recommended_human_action": rec_action
        }

        ticket = {
            "ticket_id": ticket_id,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "Open", # Open, In Progress, Resolved
            "priority": priority,
            "trigger_cause": trigger_cause,
            "student_profile": {
                "student_id": entities.get("student_id") or "Unverified",
                "student_name": entities.get("student_name") or "Student",
                "major": entities.get("major") or "Not Specified",
                "cgpa": entities.get("cgpa") or "N/A",
                "target_course": entities.get("target_course") or "N/A"
            },
            "active_topic": topic,
            "summary": structured_summary,
            "transcript": [dict(m) for m in messages],
            "advisor_notes": ""
        }

        self.tickets.append(ticket)
        return ticket

    def get_open_tickets(self) -> List[Dict[str, Any]]:
        """Returns list of open or in-progress handover tickets."""
        return [t for t in self.tickets if t["status"] in ["Open", "In Progress"]]

    def update_ticket_status(self, ticket_id: str, new_status: str, notes: str = ""):
        """Updates ticket status and advisor notes."""
        for t in self.tickets:
            if t["ticket_id"] == ticket_id:
                t["status"] = new_status
                if notes:
                    t["advisor_notes"] = notes
                return True
        return False


if __name__ == "__main__":
    from memory_manager import ConversationMemory
    
    hm = HandoverManager()
    mem = ConversationMemory()
    mem.add_message("user", "My name is David, student ID STU2025999. I'm facing debarment due to attendance!")
    mem.add_message("assistant", "Attendance requirement is 75%. You can apply for condonation if above 65%.")
    mem.add_message("user", "This is ridiculous and terrible! Connect me to a real academic advisor right now!")

    q = "This is ridiculous and terrible! Connect me to a real academic advisor right now!"
    f_score = hm.analyze_sentiment_and_friction(q)
    is_exp = hm.is_explicit_escalation_request(q)
    should, cause, prio = hm.evaluate_handover_trigger(q, confidence_score=0.35, friction_score=f_score, is_explicit=is_exp)

    print(f"Friction Score: {f_score}, Explicit: {is_exp}")
    print(f"Trigger Handover: {should} | Cause: {cause} | Priority: {prio}")

    if should:
        ticket = hm.create_handover_ticket(mem, trigger_cause=cause, priority=prio)
        print("\n--- GENERATED HANDOVER TICKET ---")
        print(f"Ticket ID: {ticket['ticket_id']} | Priority: {ticket['priority']}")
        print(f"User Issue: {ticket['summary']['user_issue']}")
        print(f"Attempted Steps: {ticket['summary']['attempted_steps']}")
        print(f"Missing Context: {ticket['summary']['missing_context']}")
        print(f"Recommended Action: {ticket['summary']['recommended_human_action']}")
