import re
import time
from typing import List, Dict, Any, Optional

class ConversationMemory:
    """
    Manages session context, entity extraction, topic stack,
    sliding window buffer, and context summaries for EduTrust AI.
    """
    def __init__(self, session_id: str = "default_session", max_window_size: int = 6):
        self.session_id = session_id
        self.max_window_size = max_window_size
        
        # Message History
        self.messages: List[Dict[str, Any]] = []
        
        # Extracted Student Entity Store
        self.entities: Dict[str, Any] = {
            "student_id": None,
            "student_name": None,
            "major": None,
            "academic_year": None,
            "cgpa": None,
            "target_course": None,
            "attendance_percentage": None,
            "escalation_requested": False
        }
        
        # Topic Stack & State
        self.current_topic: str = "General Inquiry"
        self.topic_stack: List[str] = ["General Inquiry"]
        
        # Running Context Summary for turns outside sliding window
        self.context_summary: str = ""

    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Adds a message to conversation history and updates memory state."""
        msg = {
            "role": role,
            "content": content,
            "timestamp": time.time(),
            "metadata": metadata or {}
        }
        self.messages.append(msg)
        
        if role == "user":
            self._extract_entities(content)
            self._update_topic(content)
            
        self._update_summary()

    def _extract_entities(self, text: str):
        """Regex and heuristic based extraction of student profile entities."""
        # 1. Student ID (e.g. STU2025001, ID: 12345, S1234567)
        stu_id_match = re.search(r'\b(STU\d{4,8}|ID:?\s*\d{4,8}|S\d{6,8})\b', text, re.I)
        if stu_id_match:
            self.entities["student_id"] = stu_id_match.group(0).upper()

        # 2. Student Name (e.g. My name is Alex Smith, I am Sarah)
        name_match = re.search(r'(?:my name is|i am|i\'m)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', text, re.I)
        if name_match:
            candidate = name_match.group(1).strip()
            if candidate.lower() not in ["a student", "asking", "wondering", "interested", "looking", "facing"]:
                self.entities["student_name"] = candidate.title()

        # 3. CGPA / GPA (e.g. GPA 3.4, my GPA is 2.8, CGPA of 3.9)
        gpa_match = re.search(r'\b(?:GPA|CGPA)\s*(?:is|of|=|:)?\s*([0-4]\.\d{1,2})\b', text, re.I)
        if gpa_match:
            try:
                self.entities["cgpa"] = float(gpa_match.group(1))
            except ValueError:
                pass

        # 4. Major / Department
        major_patterns = [
            (r'\b(?:computer science|cs)\b', "Computer Science"),
            (r'\b(?:data science|ds)\b', "Data Science"),
            (r'\b(?:business administration|business|finance)\b', "Business Administration"),
            (r'\b(?:mathematics|math)\b', "Mathematics"),
            (r'\b(?:artificial intelligence|ai)\b', "Artificial Intelligence")
        ]
        for pattern, major_name in major_patterns:
            if re.search(pattern, text, re.I):
                self.entities["major"] = major_name
                break

        # 5. Course Code (e.g. CS101, CS201, CS302, DS202, MATH101, BUS210, AI401)
        course_match = re.search(r'\b([A-Z]{2,4}\s?\d{3})\b', text, re.I)
        if course_match:
            self.entities["target_course"] = course_match.group(1).upper().replace(" ", "")

        # 6. Academic Year / Level
        year_patterns = [
            (r'\b(?:freshman|1st year|first year)\b', "1st Year (Freshman)"),
            (r'\b(?:sophomore|2nd year|second year)\b', "2nd Year (Sophomore)"),
            (r'\b(?:junior|3rd year|third year)\b', "3rd Year (Junior)"),
            (r'\b(?:senior|4th year|fourth year)\b', "4th Year (Senior)"),
            (r'\b(?:postgraduate|master|phd)\b', "Postgraduate")
        ]
        for pattern, yr_name in year_patterns:
            if re.search(pattern, text, re.I):
                self.entities["academic_year"] = yr_name
                break

        # 7. Attendance Percentage (e.g. 70% attendance, my attendance is 68%)
        att_match = re.search(r'\b(\d{1,2}|100)\%\s*(?:attendance)?\b', text, re.I)
        if att_match:
            try:
                self.entities["attendance_percentage"] = int(att_match.group(1))
            except ValueError:
                pass

    def _update_topic(self, text: str):
        """Identifies conversation topic and manages the topic stack for smooth resumes."""
        text_lower = text.lower()
        new_topic = None

        if any(w in text_lower for w in ["attendance", "present", "absent", "debarred", "condonation", "medical leave"]):
            new_topic = "Attendance Policy"
        elif any(w in text_lower for w in ["gpa", "cgpa", "grade", "marks", "scoring", "probation", "fail"]):
            new_topic = "Grading & Academic Standing"
        elif any(w in text_lower for w in ["course", "register", "enroll", "prerequisites", "syllabus", "add", "drop", "withdraw"]):
            new_topic = "Course Registration & Catalog"
        elif any(w in text_lower for w in ["tuition", "fee", "cost", "payment", "refund", "penalty"]):
            new_topic = "Tuition & Financials"
        elif any(w in text_lower for w in ["scholarship", "merit", "financial aid", "grant"]):
            new_topic = "Scholarships & Financial Aid"
        elif any(w in text_lower for w in ["hostel", "dorm", "room", "accommodation", "dining"]):
            new_topic = "Hostel & Campus Housing"
        elif any(w in text_lower for w in ["human", "advisor", "escalate", "agent", "person", "support team"]):
            new_topic = "Human Support Escalation"

        # Topic resume keyword check
        if any(w in text_lower for w in ["back to", "returning to", "as i was asking about", "earlier topic"]):
            if len(self.topic_stack) > 1:
                self.topic_stack.pop()
                self.current_topic = self.topic_stack[-1]
                return

        if new_topic and new_topic != self.current_topic:
            self.current_topic = new_topic
            if not self.topic_stack or self.topic_stack[-1] != new_topic:
                self.topic_stack.append(new_topic)

    def _update_summary(self):
        """Generates concise context summary when history exceeds sliding window size."""
        if len(self.messages) > self.max_window_size:
            overflow_messages = self.messages[:-self.max_window_size]
            summaries = []
            for msg in overflow_messages:
                role_label = "Student" if msg["role"] == "user" else "EduTrust AI"
                snippet = msg['content'][:100].replace('\n', ' ')
                summaries.append(f"{role_label}: {snippet}")
            
            ent_summary = ", ".join([f"{k}={v}" for k, v in self.entities.items() if v is not None])
            self.context_summary = (f"Prior Session Context Summary: {'; '.join(summaries[-4:])}. "
                                    f"Key Student Entities: [{ent_summary}]. Active Topic: {self.current_topic}.")

    def get_sliding_window_messages(self) -> List[Dict[str, Any]]:
        """Returns recent N messages within sliding window."""
        return self.messages[-self.max_window_size:]

    def get_formatted_context_for_llm(self) -> str:
        """Formats summary + entities + sliding window history into prompt context string."""
        context_parts = []
        if self.context_summary:
            context_parts.append(f"[SUMMARY OF EARLIER DIALOGUE]\n{self.context_summary}\n")
            
        known_ents = [f"{k.replace('_', ' ').title()}: {v}" for k, v in self.entities.items() if v is not None]
        if known_ents:
            context_parts.append(f"[KNOWN STUDENT PROFILE ENTITIES]\n" + "\n".join(known_ents) + "\n")

        context_parts.append(f"[CURRENT TOPIC STACK]\nCurrent Topic: {self.current_topic} | Topic History: {' -> '.join(self.topic_stack)}\n")

        recent = self.get_sliding_window_messages()
        if recent:
            context_parts.append("[RECENT DIALOGUE WINDOW]")
            for m in recent:
                sender = "Student" if m["role"] == "user" else "EduTrust AI"
                context_parts.append(f"{sender}: {m['content']}")

        return "\n".join(context_parts)

    def reset(self):
        """Resets conversation state."""
        self.messages = []
        self.entities = {k: None for k in self.entities}
        self.entities["escalation_requested"] = False
        self.current_topic = "General Inquiry"
        self.topic_stack = ["General Inquiry"]
        self.context_summary = ""


if __name__ == "__main__":
    mem = ConversationMemory()
    mem.add_message("user", "Hi, my name is Sarah, student ID STU2025088. I major in Computer Science.")
    mem.add_message("assistant", "Hello Sarah! How can I assist you with your Computer Science studies today?")
    mem.add_message("user", "I want to know about attendance requirement. My current attendance is 68%.")
    mem.add_message("assistant", "Attendance requirement is 75%. Since you are at 68%, you need medical condonation.")
    mem.add_message("user", "Okay, what about prerequisites for CS201?")
    
    print("Entities:", mem.entities)
    print("Current Topic:", mem.current_topic)
    print("Topic Stack:", mem.topic_stack)
    print("\nFormatted Context:\n", mem.get_formatted_context_for_llm())
