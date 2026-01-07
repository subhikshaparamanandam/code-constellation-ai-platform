import streamlit as st
import speech_recognition as sr
import pyttsx3
import threading
import requests
import json
import os
from datetime import date
from fpdf import FPDF

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Code Constellation",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- THEME & CSS ----------------
def local_css():
    st.markdown("""
    <style>
        /* IMPORT FONTS */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
        
        /* GENERAL SETTINGS */
        * {
            font-family: 'Outfit', sans-serif !important;
        }
        .stApp {
            background: radial-gradient(circle at 10% 20%, rgb(0, 0, 0) 0%, rgb(30, 30, 60) 90.2%);
            color: #e0e0e0;
        }
        
        /* HIDE DEFAULT ELEMENTS */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        [data-testid="stSidebar"] {display: none;}
        
        /* NAVBAR */
        .navbar {
            background: rgba(20, 20, 40, 0.6);
            backdrop-filter: blur(16px);
            padding: 1rem 1.5rem;
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        }
        .nav-logo {
            font-size: 1.8rem;
            font-weight: 700;
            background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.5px;
        }
        
        /* HERO CARD */
        .hero-card {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.01) 100%);
            backdrop-filter: blur(20px);
            padding: 4rem 2rem;
            border-radius: 24px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            text-align: center;
            margin-bottom: 3rem;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
        }
        
        /* TOPIC CARDS */
        div.stButton > button {
            width: 100%;
            height: auto;
            min-height: 120px;
            border-radius: 20px;
            background: rgba(30, 35, 50, 0.6);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            color: #f0f0f0;
            padding: 1.5rem;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            text-align: left;
            display: flex;
            flex-direction: column;
            justify-content: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        div.stButton > button:hover {
            transform: translateY(-5px) scale(1.02);
            background: rgba(40, 45, 70, 0.8);
            border-color: #00d2ff;
            box-shadow: 0 10px 25px rgba(0, 210, 255, 0.2);
            color: white;
        }
        div.stButton > button p {
            font-size: 1.3rem;
            font-weight: 600;
            margin: 0;
        }
        
        /* PROGRESS BARS */
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
        }
        
        /* CUSTOM HEADERS */
        h1, h2, h3 {
            color: #ffffff;
            font-weight: 700;
            letter-spacing: -0.5px;
        }
        
        /* INPUT FIELDS */
        .stTextInput > div > div > input {
            background-color: rgba(255, 255, 255, 0.05);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
        }
        .stTextInput > div > div > input:focus {
            border-color: #00d2ff;
            box-shadow: 0 0 10px rgba(0, 210, 255, 0.2);
        }
    </style>
    """, unsafe_allow_html=True)

local_css()

# ---------------- CONSTANTS ----------------
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"
TOPICS = ["Variables", "Data Types", "Loops", "Functions", "RAG", "LLM", "Pipelines", "AI Agents", "Embeddings"]
# TOPIC_VIDEOS removed as per user request
PASS_PERCENTAGE = 0.6
USERS_FILE = "users.json"
CERT_DIR = "certificates"
os.makedirs(CERT_DIR, exist_ok=True)

# ---------------- STATE MANAGEMENT ----------------
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "email" not in st.session_state: st.session_state.email = ""
if "view" not in st.session_state: st.session_state.view = "home"
if "current_topic" not in st.session_state: st.session_state.current_topic = None
if "doctor_code" not in st.session_state: st.session_state.doctor_code = ""

# ---------------- HELPERS ----------------
def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f: json.dump({}, f)
    with open(USERS_FILE, "r") as f: return json.load(f)

def save_users(data):
    with open(USERS_FILE, "w") as f: json.dump(data, f, indent=4)

def ask_ollama(prompt, system=None, temperature=0.7):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature}
    }
    if system:
        payload["system"] = system
        
    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=60)
        return r.json().get("response", "")
    except:
        return "⚠️ Ollama is not running."

def generate_certificate(name):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 24)
    pdf.cell(0, 20, "Code Constellation", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "", 16)
    pdf.cell(0, 10, "Certificate of Mastery", ln=True, align="C")
    pdf.ln(20)
    pdf.set_font("Arial", "", 14)
    pdf.multi_cell(0, 10, f"This certifies that\n\n{name}\n\nhas successfully mastered the fundamentals of Python & AI.\n\nDate: {date.today()}", align="C")
    path = f"{CERT_DIR}/{name.replace(' ', '_')}_certificate.pdf"
    pdf.output(path)
    return path

def rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    elif hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    else:
        # Fallback for very old/odd versions - ask user to reload
        st.error("Auto-rerun unavailable. Please refresh the page manually.")

# ---------------- VOICE UTILS ----------------
def speak_text(text):
    """Speaks the text using pyttsx3 in a thread-safe manner."""
    def _speak():
        try:
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"Speech Error: {e}")
            
    # Run in a separate thread to avoid blocking Streamlit massively, 
    # though pyttsx3 main loop requirements might still be tricky.
    # Simple execute is often safest in straightforward scripts.
    _speak()

def listen_to_user():
    """Listens to the microphone and returns the text."""
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            st.info("🎙️ Listening... Speak now!")
            audio = r.listen(source, timeout=5)
            st.success("Processing audio...")
            text = r.recognize_google(audio)
            return text
    except sr.WaitTimeoutError:
        st.warning("No speech detected.")
        return None
    except sr.RequestError:
        st.error("API unavailable.")
        return None
    except sr.UnknownValueError:
        st.warning("Could not understand audio.")
        return None
    except Exception as e:
        st.error(f"Microphone Error: {e}")
        return None

# ---------------- LABS ----------------
def render_llm_lab():
    st.subheader("🧪 Prompt Engineering Lab")
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("**Parameters**")
        temp = st.slider("Temperature (Creativity)", 0.0, 1.0, 0.7)
        system = st.text_area("System Prompt (Role)", "You are a helpful AI assistant.")
    with c2:
        st.markdown("**Testing**")
        user_input = st.text_area("User Input", "Explain quantum mechanics like I'm 5.")
        if st.button("Run Prompt"):
            with st.spinner("Generating..."):
                res = ask_ollama(user_input, system, temp)
                st.info(res)

def render_rag_lab():
    st.subheader("🔍 RAG Visualizer")
    st.markdown("See how RAG retrieves context before answering.")
    
    # Mock data for visualization since real RAG is heavy
    knowledge_base = {
        "doc1": "RAG stands for Retrieval-Augmented Generation.",
        "doc2": "LLMs can hallucinate facts if not grounded in data.",
        "doc3": "Pipelines connect data processing steps."
    }
    
    st.write("### 📚 Mini Knowledge Base")
    st.json(knowledge_base)
    
    query = st.text_input("Search Query", "What is RAG?")
    if st.button("Retrieve & Answer"):
        # Simple keyword matching simulation
        retrieved = [v for k,v in knowledge_base.items() if any(word.lower() in v.lower() for word in query.split())]
        
        if retrieved:
            context = "\n".join(retrieved)
            st.success(f"✅ Retrieved {len(retrieved)} documents")
            with st.expander("View Retrieved Context"):
                st.code(context)
            
            prompt = f"Context: {context}\n\nQuestion: {query}"
            res = ask_ollama(prompt, system="Answer using only the provided context.")
            st.markdown("### 🤖 Final Answer")
            st.write(res)
        else:
            st.warning("No relevant documents found in knowledge base.")

def render_pipeline_lab():
    st.subheader("⛓️ Pipeline Builder")
    st.markdown("Toggle stages to see how they affect the output.")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        clean = st.toggle("Phase 1: Data Cleaning", value=True)
    with col2:
        vector = st.toggle("Phase 2: Vectorization", value=True)
    with col3:
        retrieve = st.toggle("Phase 3: Retrieval", value=True)
    with col4:
        generate = st.toggle("Phase 4: Generation", value=True)
        
    st.markdown("---")
    
    if st.button("Run Pipeline"):
        log = []
        status = "Success"
        
        if clean: log.append("✅ Data Cleaned: Removed noise.")
        else: 
            log.append("❌ Data Dirty: Garbage In...")
            status = "Failed"
            
        if status == "Success" and vector: log.append("✅ Vectorized: Converted text to numbers.")
        elif status == "Success":
            log.append("❌ Vectorization Failed: Model cannot understand text.")
            status = "Failed"
            
        if status == "Success" and retrieve: log.append("✅ Retrieved: Found relevant context.")
        elif status == "Success":
            log.append("❌ Retrieval Failed: No context provided.")
            status = "Failed"
            
        if status == "Success" and generate: log.append("✅ Generated: High quality answer.")
        elif status == "Success":
            log.append("❌ Generation Failed: LLM crashed.")
            status = "Failed"
            
        for l in log: st.write(l)
        
        
        if status == "Success": st.canvas_balloons()

def render_agents_lab():
    st.subheader("🕵️ Agent Simulator")
    st.markdown("Watch an AI Agent 'think' and use tools to solve a problem.")
    
    mission = st.selectbox("Choose a Mission", ["Find current stock price", "Calculate complex math", "Book a table"])
    
    if st.button("Deploy Agent"):
        steps = []
        if mission == "Find current stock price":
            steps = [
                ("Thought", "User wants stock price. I need to search the web."),
                ("Action", "Tool: Google Search ('APPL stock price')"),
                ("Observation", "Search Result: $185.50"),
                ("Thought", "I have the answer."),
                ("Final Answer", "Apple (AAPL) is trading at $185.50.")
            ]
        elif mission == "Calculate complex math":
            steps = [
                ("Thought", "User wants to calculate 134 * 493. I should use a calculator."),
                ("Action", "Tool: Calculator(134 * 493)"),
                ("Observation", "66,062"),
                ("Final Answer", "The result is 66,062.")
            ]
        elif mission == "Book a table":
            steps = [
                ("Thought", "I need to check availability."),
                ("Action", "Tool: RestaurantAPI.check_availability('Tonight', 2 people)"),
                ("Observation", "Available: 7:00 PM, 8:30 PM"),
                ("Thought", "I will book the earlier slot."),
                ("Action", "Tool: RestaurantAPI.book('7:00 PM')"),
                ("Final Answer", "Table booked for 7:00 PM.")
            ]
            
        for s_type, content in steps:
            with st.chat_message("assistant" if s_type == "Final Answer" else "ai"):
                st.write(f"**{s_type}**: {content}")

def render_embeddings_lab():
    st.subheader("🔢 Embedding Distance")
    st.markdown("See how meaningful connections are measured mathematically.")
    
    c1, c2 = st.columns(2)
    with c1: word1 = st.text_input("Word 1", "King")
    with c2: word2 = st.text_input("Word 2", "Queen")
    
    if st.button("Calculate Similarity"):
        # improving the "simulation" to be slightly smarter using set similarity logic for fun
        # Real embeddings require heavy libraries, this is a demo
        s1 = set(word1.lower())
        s2 = set(word2.lower())
        jaccard = len(s1.intersection(s2)) / len(s1.union(s2)) if s1.union(s2) else 0.0
        
        # Artificial boost for semantic pairs (hardcoded demo magic)
        magic_pairs = [("king", "queen"), ("man", "woman"), ("apple", "fruit"), ("dog", "puppy")]
        pair = tuple(sorted((word1.lower(), word2.lower())))
        
        similarity = jaccard
        if pair in magic_pairs: similarity = 0.95
        elif word1.lower() == word2.lower(): similarity = 1.0
        
        st.metric("Semantic Similarity Score", f"{similarity:.4f}")
        st.progress(similarity)
        
        if similarity > 0.8: st.success("Very Similar!")
        elif similarity > 0.5: st.info("Somewhat Related")
        else: st.error("Not Related")



def render_code_doctor():
    if st.button("← Back to Base"):
        st.session_state.view = "home"
        rerun()
        
    st.title("🩺 AI Code Doctor")
    st.markdown("Paste your broken code below. The AI will find the bug and write a prescription.")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 🤒 Patient (Broken Code)")
        code = st.text_area("Paste code here...", height=300, value=st.session_state.doctor_code)
        st.session_state.doctor_code = code
        
        if st.button("Diagnose Bug"):
            if not code.strip():
                st.warning("Please provide some code to examine.")
            else:
                with st.spinner("Analyzing vital signs..."):
                    prompt = f"Fix this Python code and explain the bug clearly:\\n\\n```python\\n{code}\\n```"
                    res = ask_ollama(prompt, system="You are an expert Python debugger. Be concise and helpful.")
                    st.session_state.diagnosis = res
                    rerun()
                    
    with c2:
        st.markdown("### 📝 Prescription (Fix)")
        if "diagnosis" in st.session_state:
            st.markdown(st.session_state.diagnosis)
            st.success("Diagnosis Complete!")
        else:
            st.info("Waiting for patient input...")

def render_leaderboard():
    if st.button("← Back to Base"):
        st.session_state.view = "home"
        rerun()
        
    st.title("🏆 Galactic Leaderboard")
    st.markdown("Top star pilots in the galaxy.")
    
    users = load_users()
    # Sort users by topics completed (descending)
    leaderboard = []
    for email, data in users.items():
        score = len(data.get("completed_topics", []))
        leaderboard.append({"Pilot": data["name"], "Modules Mastered": score, "Rank": 0})
        
    leaderboard.sort(key=lambda x: x["Modules Mastered"], reverse=True)
    
    # Assign ranks
    for i, p in enumerate(leaderboard):
        p["Rank"] = i + 1
        
    # Display logic
    top_3 = leaderboard[:3]
    rest = leaderboard[3:]
    
    # Podium for top 3
    if top_3:
        cols = st.columns(3)
        podium_order = [1, 0, 2] # 2nd, 1st, 3rd logic for visual podium usually, but simple list is fine
        medals = ["🥇", "🥈", "🥉"]
        
        for i in range(len(top_3)):
            p = top_3[i]
            with cols[i]:
                st.markdown(f"""
                <div style="background: rgba(255,215,0,0.1); padding: 20px; border-radius: 10px; text-align: center; border: 1px solid gold;">
                    <h1>{medals[i]}</h1>
                    <h3>{p['Pilot']}</h3>
                    <p>{p['Modules Mastered']} Modules</p>
                </div>
                """, unsafe_allow_html=True)
                
    st.markdown("---")
    
    # Table for the rest
    if rest:
        st.table(rest)
    elif not leaderboard:
        st.info("No pilots found in the database.")

# ---------------- QUIZ DATA ----------------
QUIZZES = {
    "Variables": [
        ("What is a variable?", ["-- Select --", "A container", "A keyword"], "A container"),
        ("Assign symbol?", ["-- Select --", "=", "==", "!="], "="),
        ("Type style?", ["-- Select --", "Static", "Dynamic"], "Dynamic"),
        ("Valid name?", ["-- Select --", "_my_var", "1var", "var-1"], "_my_var"),
        ("Case sensitive?", ["-- Select --", "Yes", "No"], "Yes")
    ],
    "Data Types": [
        ("Text type?", ["-- Select --", "str", "int"], "str"),
        ("3.14 type?", ["-- Select --", "float", "int"], "float"),
        ("True type?", ["-- Select --", "bool", "str"], "bool"),
        ("List syntax?", ["-- Select --", "[]", "{}", "()"], "[]"),
        ("Dictionary syntax?", ["-- Select --", "{}", "[]", "()"], "{}")
    ],
    "Loops": [
        ("Loop keyword?", ["-- Select --", "for", "if"], "for"),
        ("Stop keyword?", ["-- Select --", "break", "exit"], "break"),
        ("Range(3) yields?", ["-- Select --", "0, 1, 2", "1, 2, 3"], "0, 1, 2"),
        ("While needs?", ["-- Select --", "Condition", "Counter"], "Condition"),
        ("Skip iteration?", ["-- Select --", "continue", "pass"], "continue")
    ],
    "Functions": [
        ("Define keyword?", ["-- Select --", "def", "func"], "def"),
        ("Return what?", ["-- Select --", "Value", "Nothing"], "Value"),
        ("Anonymous func?", ["-- Select --", "lambda", "delta"], "lambda"),
        ("Default argument?", ["-- Select --", "def f(x=1):", "def f(x):"], "def f(x=1):"),
        ("Call syntax?", ["-- Select --", "func()", "func"], "func()")
    ],
    "RAG": [
        ("RAG stands for?", ["-- Select --", "Retrieval-Augmented Generation", "Random AI"], "Retrieval-Augmented Generation"),
        ("RAG helps LLMs?", ["-- Select --", "External Context", "Training"], "External Context"),
        ("Vector DB stores?", ["-- Select --", "Embeddings", "Images"], "Embeddings"),
        ("Chunking is?", ["-- Select --", "Splitting text", "Merging text"], "Splitting text"),
        ("Retriever finds?", ["-- Select --", "Similar chunks", "Exact matches"], "Similar chunks")
    ],
    "LLM": [
        ("LLM is?", ["-- Select --", "Large Language Model", "Low Level Model"], "Large Language Model"),
        ("Predicts?", ["-- Select --", "Next token", "Weather"], "Next token"),
        ("Context Window?", ["-- Select --", "Memory limit", "Time limit"], "Memory limit"),
        ("Temperature 0?", ["-- Select --", "Deterministic", "Random"], "Deterministic"),
        ("Hallucination?", ["-- Select --", "False info", "Dreaming"], "False info")
    ],
    "Pipelines": [
        ("Pipelines ensure?", ["-- Select --", "Reproducibility", "Chaos"], "Reproducibility"),
        ("First step?", ["-- Select --", "Data Collection", "Deployment"], "Data Collection"),
        ("ETL stands for?", ["-- Select --", "Extract Transform Load", "Edit Text Line"], "Extract Transform Load"),
        ("Orchestrator?", ["-- Select --", "Manages flow", "Writes code"], "Manages flow"),
        ("Latency is?", ["-- Select --", "Delay", "Speed"], "Delay")
    ],
    "AI Agents": [
        ("Agents can use?", ["-- Select --", "Tools", "Magic"], "Tools"),
        ("The reasoning loop is?", ["-- Select --", "ReAct", "Sleep"], "ReAct"),
        ("Memory allows?", ["-- Select --", "Remembering past", "Forgetting"], "Remembering past"),
        ("Example tool?", ["-- Select --", "Web Search", "Thinking"], "Web Search"),
        ("Planning is?", ["-- Select --", "Breaking down goals", "Guessing"], "Breaking down goals")
    ],
    "Embeddings": [
        ("Embeddings are?", ["-- Select --", "Vectors", "Images"], "Vectors"),
        ("Used for?", ["-- Select --", "Semantic Search", "Gaming"], "Semantic Search"),
        ("High similarity?", ["-- Select --", "Close meaning", "Opposite"], "Close meaning"),
        ("Dimensions?", ["-- Select --", "Many (e.g. 1536)", "2D"], "Many (e.g. 1536)"),
        ("Dense vector?", ["-- Select --", "Non-zero values", "Zeros"], "Non-zero values")
    ]
}

# ---------------- UI COMPONENTS ----------------
def navbar(user_name=None):
    # Adjusted column ratios to prevent "Rank" text splitting
    col1, col2, col3 = st.columns([3, 4, 3])
    with col1:
        st.markdown('<div class="nav-logo">🌌 Constellation</div>', unsafe_allow_html=True)
    with col3:
        if user_name:
            c_a, c_b, c_c = st.columns(3)
            with c_a:
                if st.button("🏆 Rank", key="nav_rank"):
                    st.session_state.view = "leaderboard"
                    rerun()
            with c_b:
                if st.button("🩺 Doc", key="nav_doc"):
                    st.session_state.view = "doctor"
                    rerun()
            with c_c:
                if st.button("Exit", key="nav_logout"): # Renamed Log out to Exit for sizing
                    st.session_state.clear()
                    rerun()
        else:
            st.markdown("Guest Mode")
    st.markdown("---")

def home_view(user):
    st.markdown(f"""
    <div class="hero-card">
        <h1>Welcome Back, {user['name']} 🚀</h1>
        <p style="color: #cccccc;">Ready to continue your journey into the AI cosmos?</p>
    </div>
    """, unsafe_allow_html=True)

    completed = len(user["completed_topics"])
    total = len(TOPICS)
    progress = completed / total
    
    st.write(f"**Overall Progress: {int(progress*100)}%**")
    st.progress(progress)
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.subheader("Explore Modules")
    
    cols = st.columns(3)
    for i, t in enumerate(TOPICS):
        status = "✅" if t in user["completed_topics"] else ""
        is_unlocked = True
        
        with cols[i % 3]:
            label = f"{t}\n\n{status if is_unlocked else '🔒 Locked'}"
            if st.button(label, key=f"btn_{t}", disabled=not is_unlocked):
                st.session_state.current_topic = t
                st.session_state.view = "topic"
                rerun()
    
    st.markdown("---")
    
    # Certificate Logic (Unlocked for Demo Mode)
    if st.button("🎓 Generate Certificate"):
        if completed < total:
            st.warning(f"Note: You have completed {completed}/{total} topics. This is a provisional certificate.")
        path = generate_certificate(user["name"])
        with open(path, "rb") as f:
            st.download_button("Download PDF", f, file_name="certificate.pdf")
            
    if completed == total:
        st.success("🎉 You have mastered the constellation!")

def topic_view(user, topic):
    if st.button("← Back to Roadmap"):
        st.session_state.view = "home"
        rerun()
        
    st.title(f"📘 {topic}")
    
    # Check if topic has a lab
    has_lab = topic in ["LLM", "RAG", "Pipelines", "AI Agents", "Embeddings"]
    tabs = ["📖 Learn", "🤖 AI Tutor", "📝 Quiz"]
    if has_lab: tabs.append("🛠️ Lab")
    
    active_tab = st.tabs(tabs)
    
    with active_tab[0]:
        st.markdown("### Core Concepts")
            
        # Try to load markdown content if exists, else fallback to AI
        try:
            with open(f"Content/{topic.lower().replace(' ', '_')}.md", "r") as f:
                st.markdown(f.read(), unsafe_allow_html=True)
        except:
            if st.button("Generate Lesson with AI"):
                with st.spinner("Consulting the stars..."):
                    st.markdown(ask_ollama(f"Explain {topic} in Python for beginners."))
    
    with active_tab[1]:
        st.markdown("### Ask Anything")
        
        # Voice Toggle
        use_voice = st.checkbox("Enable Voice Mode 🎙️")
        
        if use_voice:
            if st.button("🎙️ Speak Question"):
                question_text = listen_to_user()
                if question_text:
                    st.write(f"**You said:** {question_text}")
                    with st.spinner("Thinking..."):
                        response = ask_ollama(question_text)
                        st.write(response)
                        speak_text(response)
        
        else:
            q = st.text_input("Your question:")
            if st.button("Ask AI"):
                with st.spinner("Thinking..."):
                    st.write(ask_ollama(q))
                
    with active_tab[2]:
        st.markdown("### Knowledge Check")
        score = 0
        qs = QUIZZES.get(topic, [])
        answers = []
        for i, (q_text, options, correct) in enumerate(qs):
            ans = st.radio(q_text, options, key=f"q_{topic}_{i}")
            if ans == correct: score += 1
            answers.append(ans)
            
        if st.button("Submit Quiz"):
            if "-- Select --" in answers:
                st.warning("Please answer all questions.")
            elif score / len(qs) >= PASS_PERCENTAGE:
                st.balloons()
                st.success(f"Passed! {score}/{len(qs)}")
                if topic not in user["completed_topics"]:
                    user["completed_topics"].append(topic)
                    save_users(users)
            else:
                st.error(f"Score: {score}/{len(qs)}. Try again!")
                
    if has_lab:
        with active_tab[3]:
            if topic == "LLM": render_llm_lab()
            elif topic == "RAG": render_rag_lab()
            elif topic == "Pipelines": render_pipeline_lab()
            elif topic == "AI Agents": render_agents_lab()
            elif topic == "Embeddings": render_embeddings_lab()

# ---------------- MAIN APP ----------------
if not st.session_state.logged_in:
    navbar()
    st.markdown("<div class='hero-card'><h1>🔐 Login to Code Constellation</h1></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        name = st.text_input("Name")
        email = st.text_input("Email")
        if st.button("Start Journey", use_container_width=True):
            if name and email:
                users = load_users()
                if email not in users:
                    users[email] = {"name": name, "completed_topics": []}
                    save_users(users)
                st.session_state.logged_in = True
                st.session_state.email = email

                rerun()
else:
    users = load_users()
    user = users[st.session_state.email]
    navbar(user["name"])
    
    if st.session_state.view == "home":
        home_view(user)
    elif st.session_state.view == "topic":
        topic_view(user, st.session_state.current_topic)
    elif st.session_state.view == "doctor":
        render_code_doctor()
    elif st.session_state.view == "leaderboard":
        render_leaderboard()
