import streamlit as st
import streamlit.components.v1 as components
import os
import json
from layers.orchestration_v2 import SiliconBrainPhase3
from layers.visualizer import BrainVisualizer
from layers.graph_connector import MemgraphConnector

# --- CONFIGURATION & SESSION STATE ---
st.set_page_config(page_title="SiliconBrain Control Center", layout="wide", page_icon="🧠")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "brain" not in st.session_state:
    st.session_state.brain = SiliconBrainPhase3()

# --- BACKGROUND INGESTOR SERVICE ---
import sys
if not hasattr(sys, "_siliconbrain_ingestor_started"):
    sys._siliconbrain_ingestor_started = True
    import threading
    from layers.ingestor import HungryBrain
    if not os.path.exists("data/ingest"):
        os.makedirs("data/ingest")
        
    def run_ingestor():
        try:
            hb = HungryBrain()
            hb.watch(once=False)
        except Exception as e:
            print(f"[INGESTOR THREAD] Ingestor watch failed: {e}")
            
    t = threading.Thread(target=run_ingestor, daemon=True)
    t.start()

# --- HELPER FUNCTIONS ---
def refresh_brain_map():
    viz = BrainVisualizer()
    viz.generate_map()

# --- UI LAYOUT ---
st.title("🧠 SiliconBrain Dashboard")
st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["💬 Brain Chat", "🗺️ Knowledge Map", "📤 Ingest Library", "🎓 Master Domain"])

# --- TAB 1: CHAT ---
with tab1:
    st.header("Chat with your Silicon Brain")
    
    # Display conversation history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and message.get("metrics"):
                metrics = message["metrics"]
                with st.expander("📊 Comparative Token Efficiency Report", expanded=False):
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Dense Baseline", f"{metrics['baseline_total']} t")
                    col2.metric("Sparse Graph", f"{metrics['sparse_total']} t")
                    col3.metric("Tokens Saved", f"{metrics['savings']} t")
                    col4.metric("Reduction", f"{metrics['reduction_ratio']}%")
                    st.caption(f"🔋 Energy Profile: {metrics['energy_profile']}")

    # Chat Input
    if prompt := st.chat_input("Ask me anything about your project..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # Format conversational history
            chat_history = []
            for msg in st.session_state.messages[:-1]:
                chat_history.append({"role": msg["role"], "content": msg["content"]})
            
            # Initialize the brain state
            inputs = {
                "user_input": prompt,
                "chat_history": chat_history,
                "history": [],
                "thought_process": [],
                "graph_results": []
            }
            
            # Use a status container for the 'Thinking Process'
            with st.status("Thinking...", expanded=True) as status:
                # We need a custom invoke to stream thoughts
                # For now, we'll run it and display thoughts after
                result = st.session_state.brain.build_graph().invoke(inputs)
                
                for thought in result.get("thought_process", []):
                    st.write(f"🔍 {thought}")
                status.update(label="Reasoning Complete", state="complete", expanded=False)

            # Final response
            response = result.get("final_response", "I encountered an error during reasoning.")
            metrics = result.get("efficiency_metrics")
            st.markdown(response)
            
            if metrics:
                with st.expander("📊 Comparative Token Efficiency Report", expanded=True):
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Dense Baseline", f"{metrics['baseline_total']} t")
                    col2.metric("Sparse Graph", f"{metrics['sparse_total']} t")
                    col3.metric("Tokens Saved", f"{metrics['savings']} t")
                    col4.metric("Reduction", f"{metrics['reduction_ratio']}%")
                    st.caption(f"🔋 Energy Profile: {metrics['energy_profile']} (Local Ollama vs Cloud Dense)")
            
            st.session_state.messages.append({"role": "assistant", "content": response, "metrics": metrics})

# --- TAB 2: BRAIN MAP ---
with tab2:
    st.header("Interactive Knowledge Graph")
    col1, col2 = st.columns([1, 6])
    
    with col1:
        if st.button("🔄 Refresh Map"):
            with st.spinner("Regenerating graph..."):
                refresh_brain_map()
            st.success("Map Updated!")

    with col2:
        if os.path.exists("brain_map.html"):
            with open("brain_map.html", 'r', encoding='utf-8') as f:
                html_data = f.read()
            components.html(html_data, height=800, scrolling=True)
        else:
            st.info("No brain map found. Click 'Refresh Map' to generate one.")

# --- TAB 3: INGEST ---
with tab3:
    st.header("Upload Documents to Memory")
    st.markdown("Drop .txt or .md files here to feed them to your Silicon Brain.")
    
    uploaded_files = st.file_uploader("Choose documentation files", type=['md', 'txt'], accept_multiple_files=True)
    
    if uploaded_files:
        if not os.path.exists("data/ingest"):
            os.makedirs("data/ingest")
            
        for uploaded_file in uploaded_files:
            file_path = os.path.join("data/ingest", uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"File '{uploaded_file.name}' uploaded to data/ingest/ and queued for learning.")
            
    st.info("The background Ingestor service will automatically process these files every 10 seconds.")

# --- TAB 4: MASTERY ---
with tab4:
    st.header("Recursive Domain Mastery")
    st.markdown("Enter a broad topic, and the SiliconBrain will recursively interrogate the Teacher to build a complete knowledge tree.")
    
    mastery_topic = st.text_input("Topic to Master", placeholder="e.g., Quantum Computing, Android Internals...")
    depth = st.slider("Depth of Recursion", min_value=1, max_value=3, value=1)
    
    if st.button("🚀 Start Mastery Loop"):
        if not mastery_topic:
            st.error("Please enter a topic.")
        else:
            from layers.mastery import MasteryEngine
            engine = MasteryEngine()
            
            with st.status(f"Mastering {mastery_topic}...", expanded=True) as status:
                st.write(f"Initiating recursive loop with depth {depth}...")
                # We'll run a simplified version here for the UI
                engine.master_topic(mastery_topic, depth=depth, max_per_level=2)
                status.update(label=f"Mastery of {mastery_topic} Complete!", state="complete")
            st.success(f"Knowledge tree for '{mastery_topic}' has been integrated into the graph.")
            refresh_brain_map()
