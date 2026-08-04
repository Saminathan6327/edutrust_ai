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
    /* Import Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global Body Font & Background overrides */
    .stApp {
        background-color: #F5F2EB !important;
        font-family: 'Inter', sans-serif !important;
        color: #1A1A1A !important;
    }

    /* Sidebar Background & Border */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #D3D3D3 !important;
    }
    [data-testid="stSidebar"] * {
        font-family: 'Inter', sans-serif !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4 {
        font-family: 'Playfair Display', Georgia, serif !important;
        color: #1A1A1A !important;
        font-weight: 600 !important;
    }

    /* Header styling matching Cognita Quill */
    .main-header {
        font-family: 'Playfair Display', Georgia, serif !important;
        font-size: 2.3rem !important;
        color: #1A1A1A !important;
        font-weight: 800 !important;
        text-align: center !important;
        text-transform: uppercase !important;
        letter-spacing: 0.12em !important;
        margin-top: 10px !important;
        margin-bottom: 5px !important;
        border-top: 2px solid #1A1A1A !important;
        border-bottom: 1px solid #1A1A1A !important;
        padding: 18px 0 !important;
    }
    .sub-header {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.8rem !important;
        color: #666666 !important;
        text-align: center !important;
        text-transform: uppercase !important;
        letter-spacing: 0.18em !important;
        margin-bottom: 25px !important;
        font-weight: 500 !important;
        border-bottom: 1px solid #E6E2D8 !important;
        padding-bottom: 15px !important;
    }

    /* Academic Headings */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Playfair Display', Georgia, serif !important;
        color: #1A1A1A !important;
        font-weight: 600 !important;
    }

    /* Tabs Styling - Wix Category Navigation Menu Style */
    .stTabs [data-baseweb="tab-list"] {
        gap: 30px !important;
        border-bottom: 1px solid #D3D3D3 !important;
        justify-content: center !important;
        margin-bottom: 25px !important;
        background-color: transparent !important;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        color: #666666 !important;
        background-color: transparent !important;
        border: none !important;
        padding: 0 12px !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #1A1A1A !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #1A1A1A !important;
        font-weight: 700 !important;
        border-bottom: 2px solid #1A1A1A !important;
    }

    /* Metrics Container Styling */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF !important;
        border: 1px solid #D3D3D3 !important;
        border-radius: 4px !important;
        padding: 15px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.02) !important;
        text-align: center !important;
        transition: transform 0.2s ease !important;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 15px rgba(0,0,0,0.04) !important;
    }
    div[data-testid="metric-container"] [data-testid="stMetricLabel"] {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.75rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        color: #666666 !important;
        justify-content: center !important;
    }
    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-family: 'Playfair Display', Georgia, serif !important;
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        color: #1A1A1A !important;
    }

    /* Expander / Ticket Card Styling */
    div[data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border: 1px solid #D3D3D3 !important;
        border-radius: 4px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.02) !important;
        margin-bottom: 15px !important;
        overflow: hidden !important;
    }
    div[data-testid="stExpander"] summary {
        font-family: 'Playfair Display', Georgia, serif !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        color: #1A1A1A !important;
        background-color: #FFFFFF !important;
        padding: 15px !important;
        transition: background-color 0.2s ease !important;
    }
    div[data-testid="stExpander"] summary:hover {
        background-color: #FAF9F6 !important;
    }
    div[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        border-top: 1px solid #E6E2D8 !important;
        padding: 20px !important;
        background-color: #FAF9F6 !important;
    }

    /* Flat Solid & Outline Buttons */
    div.stButton > button {
        background-color: #1A1A1A !important;
        color: #FFFFFF !important;
        border: 1px solid #1A1A1A !important;
        border-radius: 4px !important;
        padding: 8px 20px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
    }
    div.stButton > button:hover {
        background-color: #FFFFFF !important;
        color: #1A1A1A !important;
        border-color: #1A1A1A !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
    }
    /* Accent Terracotta button for Escalation */
    div.stButton > button[kind="primary"] {
        background-color: #8C2D19 !important;
        border-color: #8C2D19 !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #FFFFFF !important;
        color: #8C2D19 !important;
        border-color: #8C2D19 !important;
    }

    /* Inputs, Selectboxes, Textareas styling */
    div[data-baseweb="input"], div[data-baseweb="textarea"], div[data-baseweb="select"] {
        background-color: #FFFFFF !important;
        border: 1px solid #D3D3D3 !important;
        border-radius: 4px !important;
        font-family: 'Inter', sans-serif !important;
        color: #1A1A1A !important;
    }
    div[data-baseweb="input"] input, div[data-baseweb="textarea"] textarea {
        color: #1A1A1A !important;
    }

    /* Chat Messages Styling */
    div[data-testid="stChatMessage"] {
        background-color: #FFFFFF !important;
        border: 1px solid #D3D3D3 !important;
        border-radius: 4px !important;
        padding: 16px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.01) !important;
    }
    div[data-testid="stChatMessage"][data-is-user="true"] {
        background-color: #FAF9F6 !important;
        border-left: 3px solid #1A1A1A !important;
    }

    /* Custom Cards */
    .sidebar-card {
        background-color: #FAF9F6 !important;
        border: 1px solid #E6E2D8 !important;
        border-radius: 4px !important;
        padding: 16px !important;
        margin-bottom: 18px !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.01) !important;
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
    ents = memory.entities
    att_str = f"{ents['attendance_percentage']}%" if ents.get('attendance_percentage') else 'N/A'
    profile_html = f"""
    <div class="sidebar-card">
        <h4 style="margin-top:0; margin-bottom:12px; font-family:'Playfair Display', Georgia, serif; font-size:1.1rem; border-bottom:1px solid #E6E2D8; padding-bottom:6px;">Extracted Profile</h4>
        <p style="margin: 6px 0; font-size:0.85rem;">👤 <strong>Name</strong>: {ents.get('student_name') or 'Anonymous'}</p>
        <p style="margin: 6px 0; font-size:0.85rem;">🆔 <strong>Student ID</strong>: <code style="font-size:0.75rem; background: #E6E2D8; padding: 2px 4px; border-radius: 2px;">{ents.get('student_id') or 'Not Extracted'}</code></p>
        <p style="margin: 6px 0; font-size:0.85rem;">📚 <strong>Major</strong>: {ents.get('major') or 'Not Specified'}</p>
        <p style="margin: 6px 0; font-size:0.85rem;">🎓 <strong>CGPA</strong>: {ents.get('cgpa') or 'N/A'}</p>
        <p style="margin: 6px 0; font-size:0.85rem;">📖 <strong>Target Course</strong>: <code style="font-size:0.75rem; background: #E6E2D8; padding: 2px 4px; border-radius: 2px;">{ents.get('target_course') or 'N/A'}</code></p>
        <p style="margin: 6px 0; font-size:0.85rem;">📊 <strong>Attendance</strong>: {att_str}</p>
    </div>
    """
    st.markdown(profile_html, unsafe_allow_html=True)

    # Live AI Trust & Confidence Meter
    conf = st.session_state.last_metrics["confidence_score"]
    level = st.session_state.last_metrics["confidence_level"]
    ground = st.session_state.last_metrics["groundedness_score"]
    frict = st.session_state.last_metrics["friction_score"]

    meters_html = f"""
    <div class="sidebar-card">
        <h4 style="margin-top:0; margin-bottom:12px; font-family:'Playfair Display', Georgia, serif; font-size:1.1rem; border-bottom:1px solid #E6E2D8; padding-bottom:6px;">AI Trust & Safety</h4>
        <div style="margin: 10px 0;">
            <div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:3px;">
                <span><strong>Confidence Level</strong></span>
                <span style="font-family:monospace; background:#1A1A1A; color:#FFF; padding:1px 4px; border-radius:2px; font-size:0.75rem;">{level}</span>
            </div>
            <div style="background:#E6E2D8; height:6px; border-radius:3px; overflow:hidden;">
                <div style="background:#1A1A1A; height:100%; width:{conf*100}%;"></div>
            </div>
        </div>
        <div style="margin: 10px 0;">
            <div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:3px;">
                <span><strong>RAG Groundedness</strong></span>
                <span style="font-family:monospace; font-size:0.75rem;">{ground*100:.0f}%</span>
            </div>
            <div style="background:#E6E2D8; height:6px; border-radius:3px; overflow:hidden;">
                <div style="background:#1A1A1A; height:100%; width:{ground*100}%;"></div>
            </div>
        </div>
        <div style="margin: 10px 0;">
            <div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:3px;">
                <span><strong>Frustration / Friction</strong></span>
                <span style="font-family:monospace; font-size:0.75rem;">{frict*100:.0f}%</span>
            </div>
            <div style="background:#E6E2D8; height:6px; border-radius:3px; overflow:hidden;">
                <div style="background:#8C2D19; height:100%; width:{frict*100}%;"></div>
            </div>
        </div>
    </div>
    """
    st.markdown(meters_html, unsafe_allow_html=True)

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

