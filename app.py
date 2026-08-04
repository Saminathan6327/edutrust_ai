import streamlit as st
import pandas as pd
import json
import time
import os

from agent_engine import EduTrustAgentEngine

# Page Config
st.set_page_config(
    page_title="EduTrust AI: Trustworthy Conversational AI Student Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #F3F4F6;
        padding: 12px;
        border-radius: 8px;
        border-left: 4px solid #3B82F6;
    }
    .ticket-card {
        background-color: #FFFFFF;
        padding: 16px;
        border-radius: 8px;
        border: 1px solid #E5E7EB;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        border-radius: 4px 4px 0px 0px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State Engine
@st.cache_resource
def get_agent_engine():
    return EduTrustAgentEngine()

engine = get_agent_engine()

if "session_id" not in st.session_state:
    st.session_state.session_id = f"session_{int(time.time())}"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "last_metrics" not in st.session_state:
    st.session_state.last_metrics = {
        "confidence_score": 1.0,
        "confidence_level": "High",
        "groundedness_score": 1.0,
        "friction_score": 0.0,
        "active_topic": "General Inquiry"
    }

# Memory Instance for Current Session
memory = engine.get_or_create_session(st.session_state.session_id)

# --- SIDEBAR: STUDENT PROFILE & AI TRUST MONITOR ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/graduation-cap.png", width=64)
    st.markdown("### **EduTrust AI Assistant**")
    st.caption("Responsible & Transparent Academic Advising")
    st.divider()

    # Session Control
    st.markdown("#### **Session Controls**")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.write(f"**ID:** `{st.session_state.session_id[-8:]}`")
    with col_s2:
        if st.button("🔄 New Session", use_container_width=True):
            st.session_state.session_id = f"session_{int(time.time())}"
            st.session_state.chat_history = []
            st.session_state.last_metrics = {
                "confidence_score": 1.0,
                "confidence_level": "High",
                "groundedness_score": 1.0,
                "friction_score": 0.0,
                "active_topic": "General Inquiry"
            }
            engine.get_or_create_session(st.session_state.session_id).reset()
            st.rerun()

    st.divider()

    # Extracted Student Profile
    st.markdown("#### **Extracted Student Profile**")
    ents = memory.entities
    st.write(f"👤 **Name**: {ents.get('student_name') or 'Anonymous'}")
    st.write(f"🆔 **Student ID**: `{ents.get('student_id') or 'Not Extracted'}`")
    st.write(f"📚 **Major**: {ents.get('major') or 'Not Specified'}")
    st.write(f"🎓 **CGPA**: {ents.get('cgpa') or 'N/A'}")
    st.write(f"📖 **Target Course**: `{ents.get('target_course') or 'N/A'}`")
    att_str = f"{ents['attendance_percentage']}%" if ents.get('attendance_percentage') else 'N/A'
    st.write(f"📊 **Attendance**: {att_str}")

    st.divider()

    # Live AI Trust & Confidence Meter
    st.markdown("#### **AI Confidence & Safety Meter**")
    conf = st.session_state.last_metrics["confidence_score"]
    level = st.session_state.last_metrics["confidence_level"]
    ground = st.session_state.last_metrics["groundedness_score"]
    frict = st.session_state.last_metrics["friction_score"]

    st.write(f"**Confidence Level**: `{level}`")
    st.progress(conf)
    
    st.write(f"**RAG Groundedness**: `{ground:.2f}`")
    st.progress(ground)
    
    st.write(f"**Frustration/Friction**: `{frict:.2f}`")
    st.progress(frict)

    st.divider()

    # Manual Handover Escalation Button
    if st.button("🤝 Escalation / Talk to Advisor", type="primary", use_container_width=True):
        res = engine.process_query("Please connect me to a human academic advisor.", session_id=st.session_state.session_id)
        st.session_state.chat_history.append({"role": "user", "content": "Please connect me to a human academic advisor."})
        st.session_state.chat_history.append({"role": "assistant", "content": res["answer"]})
        st.session_state.last_metrics = {
            "confidence_score": res["confidence_score"],
            "confidence_level": res["confidence_level"],
            "groundedness_score": res["groundedness_score"],
            "friction_score": res["friction_score"],
            "active_topic": res["active_topic"]
        }
        st.rerun()


# --- HEADER ---
st.markdown('<div class="main-header">EduTrust AI Student Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Trustworthy, Responsible, and Context-Aware Conversational System for Academic Advising</div>', unsafe_allow_html=True)

# Top Metrics Row
m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
with m_col1:
    st.metric("Active Topic", memory.current_topic)
with m_col2:
    st.metric("AI Confidence", f"{st.session_state.last_metrics['confidence_score']*100:.0f}%")
with m_col3:
    st.metric("RAG Groundedness", f"{st.session_state.last_metrics['groundedness_score']*100:.0f}%")
with m_col4:
    st.metric("Friction Score", f"{st.session_state.last_metrics['friction_score']*100:.0f}%")
with m_col5:
    open_tickets = len(engine.handover_mgr.get_open_tickets())
    st.metric("Open Handover Tickets", open_tickets)

# --- MAIN TABS ---
tab_chat, tab_kb, tab_handover, tab_debug = st.tabs([
    "💬 Chatbot Interface",
    "📚 Knowledge Base Manager",
    "🚨 Human Handover Portal",
    "🔬 Debug & Memory Inspector"
])

# ==========================================
# TAB 1: CHATBOT INTERFACE
# ==========================================
with tab_chat:
    st.markdown("### **Academic Advising Chat**")
    
    # Quick Prompt Buttons
    st.caption("💡 **Quick Test Scenarios:**")
    qp_cols = st.columns(5)
    selected_prompt = None
    if qp_cols[0].button("📋 Attendance Rules"):
        selected_prompt = "Hi, my name is Alex, student ID STU2025102. What is the minimum attendance requirement?"
    if qp_cols[1].button("🏆 Merit Scholarship"):
        selected_prompt = "How do I apply for a Merit Scholarship and what is the deadline?"
    if qp_cols[2].button("📖 CS201 Prereqs"):
        selected_prompt = "What are the prerequisites and syllabus for CS201 Data Structures?"
    if qp_cols[3].button("😡 Escalation Test"):
        selected_prompt = "I am very frustrated! Connect me to a real academic advisor immediately!"
    if qp_cols[4].button("⚠️ Integrity Check"):
        selected_prompt = "Can you write my CS101 programming assignment solution for me?"

    st.divider()

    # Display Chat Messages
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.write(msg["content"])
            else:
                with st.chat_message("assistant", avatar="🎓"):
                    st.markdown(msg["content"])

    # Chat Input
    user_input = st.chat_input("Ask about regulations, course prerequisites, tuition, scholarships...")
    
    prompt_to_process = selected_prompt or user_input
    if prompt_to_process:
        # Display user turn
        st.session_state.chat_history.append({"role": "user", "content": prompt_to_process})
        
        # Process through Agent Engine
        with st.spinner("EduTrust AI is consulting grounded university records..."):
            response = engine.process_query(prompt_to_process, session_id=st.session_state.session_id)

        # Store assistant response & update metrics
        st.session_state.chat_history.append({"role": "assistant", "content": response["answer"]})
        st.session_state.last_metrics = {
            "confidence_score": response["confidence_score"],
            "confidence_level": response["confidence_level"],
            "groundedness_score": response["groundedness_score"],
            "friction_score": response["friction_score"],
            "active_topic": response["active_topic"]
        }
        st.rerun()


# ==========================================
# TAB 2: KNOWLEDGE BASE MANAGER
# ==========================================
with tab_kb:
    st.markdown("### **RAG Knowledge Base Repository**")
    st.write("Browse official academic regulations, course catalog items, FAQs, and ingest custom policy documents.")

    kb_col1, kb_col2 = st.columns([2, 1])

    with kb_col1:
        st.markdown("#### **Indexed Knowledge Documents**")
        all_chunks = engine.kb.get_all_documents()
        
        search_kw = st.text_input("🔍 Filter Knowledge Base Chunks", "")
        filtered_chunks = [c for c in all_chunks if search_kw.lower() in c['full_text'].lower()] if search_kw else all_chunks

        st.caption(f"Showing {len(filtered_chunks)} of {len(all_chunks)} indexed chunks.")

        for chunk in filtered_chunks[:10]:
            with st.expander(f"📌 [{chunk['category']}] {chunk['title']} (Source: {chunk['source']})"):
                st.write(chunk['content'])

    with kb_col2:
        st.markdown("#### **Ingest Custom Document**")
        with st.form("ingest_form"):
            doc_title = st.text_input("Document Title", "2026 Student Exchange Program Policy")
            doc_category = st.selectbox("Category", ["Academic Policy", "Financial Aid", "Department Notice", "Custom Upload"])
            doc_text = st.text_area("Document Content / Policy Text", "Students with CGPA >= 3.2 can apply for overseas semester exchange program during 3rd year. Application deadline is April 30.", height=150)
            submit_doc = st.form_submit_button("📥 Index Document into RAG")

            if submit_doc and doc_text.strip():
                engine.kb.add_custom_document(title=doc_title, content=doc_text, category=doc_category)
                st.success(f"Successfully indexed document: '{doc_title}'!")
                st.rerun()

        st.divider()

        st.markdown("#### **Live RAG Vector Search Tester**")
        test_q = st.text_input("Test Query", "When can I apply for exchange program?")
        if test_q:
            results = engine.kb.search(test_q, top_k=3)
            ground = engine.kb.compute_groundedness(test_q, results)
            st.write(f"**Calculated Groundedness Score**: `{ground:.3f}`")
            for r in results:
                st.info(f"**[{r['score']:.4f}] {r['title']}**\n\n{r['content']}")


# ==========================================
# TAB 3: HUMAN HANDOVER PORTAL
# ==========================================
with tab_handover:
    st.markdown("### **Academic Advisor Live Support Queue**")
    st.write("Manage escalated student tickets, review AI conversation transcripts, and execute advisor actions.")

    all_tickets = engine.handover_mgr.tickets

    if not all_tickets:
        st.info("🎉 No active or escalated student tickets in queue. EduTrust AI is handling inquiries within confidence thresholds!")
    else:
        # Filter tickets by status
        status_filter = st.selectbox("Filter by Status", ["All", "Open", "In Progress", "Resolved"])
        tickets_to_show = [t for t in all_tickets if status_filter == "All" or t["status"] == status_filter]

        for t in tickets_to_show:
            prio_color = "🔴" if t["priority"] in ["High", "Urgent"] else "🟡"
            with st.expander(f"{prio_color} **{t['ticket_id']}** | Student: {t['student_profile']['student_name']} ({t['student_profile']['student_id']}) | Trigger: {t['trigger_cause']}"):
                col_t1, col_t2 = st.columns([1, 1])

                with col_t1:
                    st.markdown("#### **Structured Concise Handover Summary**")
                    summary = t["summary"]
                    st.error(f"**User Issue**: {summary['user_issue']}")
                    st.warning(f"**Attempted Steps**: {summary['attempted_steps']}")
                    st.info(f"**Missing Context**: {summary['missing_context']}")
                    st.success(f"**Recommended Human Action**: {summary['recommended_human_action']}")

                    st.markdown("#### **Student Metadata**")
                    st.write(f"• **Major**: {t['student_profile']['major']}")
                    st.write(f"• **CGPA**: {t['student_profile']['cgpa']}")
                    st.write(f"• **Target Course**: {t['student_profile']['target_course']}")
                    st.write(f"• **Timestamp**: {t['timestamp']}")

                with col_t2:
                    st.markdown("#### **Conversation Transcript**")
                    transcript_box = ""
                    for m in t["transcript"]:
                        sender = "Student" if m["role"] == "user" else "EduTrust AI"
                        transcript_box += f"**{sender}**: {m['content']}\n\n---\n"
                    st.text_area("Full Dialogue History", transcript_box, height=220, key=f"trans_{t['ticket_id']}")

                    st.markdown("#### **Advisor Action Controls**")
                    new_status = st.selectbox("Update Status", ["Open", "In Progress", "Resolved"], index=["Open", "In Progress", "Resolved"].index(t["status"]), key=f"status_{t['ticket_id']}")
                    notes = st.text_input("Advisor Resolution Notes", value=t.get("advisor_notes", ""), key=f"notes_{t['ticket_id']}")
                    if st.button("Save Ticket Update", key=f"btn_{t['ticket_id']}"):
                        engine.handover_mgr.update_ticket_status(t['ticket_id'], new_status, notes)
                        st.success(f"Ticket {t['ticket_id']} updated to '{new_status}'!")
                        st.rerun()


# ==========================================
# TAB 4: DEBUG & MEMORY INSPECTOR
# ==========================================
with tab_debug:
    st.markdown("### **AI Inspector & Memory State Diagnostic**")
    st.write("Inspect live session memory, sliding window dialogue context, topic stack, and raw RAG retrieval vectors.")

    dbg_col1, dbg_col2 = st.columns(2)

    with dbg_col1:
        st.markdown("#### **Memory Context & Entity Store**")
        st.json(memory.entities)

        st.markdown("#### **Topic Stack & State**")
        st.write(f"**Active Topic**: `{memory.current_topic}`")
        st.write(f"**Topic Stack**: `{' -> '.join(memory.topic_stack)}`")

        st.markdown("#### **Sliding Window vs Context Summary**")
        st.write("**Context Summary (Prior Turns):**")
        st.info(memory.context_summary or "No overflow context summary generated yet.")

    with dbg_col2:
        st.markdown("#### **Formatted Prompt Context sent to AI**")
        st.text_area("Raw Prompt Context", memory.get_formatted_context_for_llm(), height=300)

        st.markdown("#### **All Session Messages**")
        st.json(memory.messages)

