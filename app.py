import streamlit as st
import json
from groq import Groq
import os
import time

from datetime import datetime
import config
from utils import get_whatsapp_link, generate_share_text, calculate_match_score
from dotenv import load_dotenv
import csv


# Load environment variables

# Load environment variables
load_dotenv()

# SAFETY: Check for API Key
if not os.getenv("GROQ_API_KEY"):
    st.error("🔑 Please set GROQ_API_KEY in your .env file")
    st.stop()

# -------------------------------------------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------------------------------------------
def save_lead(data):
    """Save lead data to CSV"""
    file_exists = os.path.isfile("leads.csv")
    with open("leads.csv", "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Name", "Role", "Challenge", "Goal", "Program"])
        writer.writerow([
            datetime.now(), 
            data['name'], 
            data['role'], 
            data['challenge'], 
            data['goal'],
            data.get('program', 'N/A')
        ])

@st.cache_data(ttl=3600)
def generate_roadmap(user_data, version, language):
    """Generate roadmap using AI with caching"""
    try:
        # Robust API Key Retrieval
        # Priority: 1. Streamlit Cloud Secrets (st.secrets) 2. Environment Variable (os.getenv)
        api_key = None
        if "GROQ_API_KEY" in st.secrets:
            api_key = st.secrets["GROQ_API_KEY"]
        else:
            api_key = os.getenv("GROQ_API_KEY")
            
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in secrets or environment.")

        client = Groq(api_key=api_key)
        
        lang = config.LANGUAGES[language]["name"]
        tone = "urgent sales with FOMO and scarcity" if version == "B" else "warm supportive mentoring"

        prompt = f"""
You are Asha, an AI Leadership Architect for Iron Lady. Speak in {lang}.

User Profile:
- Name: {user_data['name']}
- Current Stage: {user_data['role']}
- Challenge: {user_data['challenge']}
- Goal: {user_data['goal']}

Available Programs:
{json.dumps(config.PROGRAMS_DB, indent=2)}

Tone: {tone}

Create a personalized roadmap with:

1. **Best Program Match** (with % match score 85-95%)
2. **Why This Program** (emotional connection to their goal)
3. **Alternate Option** (if primary doesn't fit)
4. **3-Step Transformation Plan**
5. **Expected Outcomes** (specific, measurable)
6. **Comparison Table** (Best vs Alternate - Duration, Focus, Price)
7. **Emotional CTA** (call to action)

Format with markdown. Be specific to their profile. Use their name.
"""
        out = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1200
        )
        return out.choices[0].message.content
    except Exception as e:
        # DEBUG: Show actual error to the user
        st.error(f"⚠️ Debug Error: {str(e)}")
        
        # FALLBACK RESPONSE
        return f"""
### ⚠️ AI Service Busy - Using Backup Roadmap

**Recommended Program: Leadership Accelerator**

Based on your goal to "{user_data['goal']}", this 6-month program is the best fit.

*   **Match Score**: 92%
*   **Focus**: Strategic Leadership & Team Management
*   **Outcome**: Executive Presence & C-Suite Readiness

Please contact our counselors for a more detailed plan.
"""


# -------------------------------------------------------------------------------------
# PAGE CONFIGURATION
# -------------------------------------------------------------------------------------
st.set_page_config(
    page_title="Iron Lady: Leadership Navigator - AI Powered",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# -------------------------------------------------------------------------------------
if "stage" not in st.session_state: st.session_state.stage = 0
if "user_data" not in st.session_state: st.session_state.user_data = {}
if "ai_response" not in st.session_state: st.session_state.ai_response = ""
if "progress" not in st.session_state: st.session_state.progress = 25
if "ab_test_version" not in st.session_state: st.session_state.ab_test_version = "A"
if "language" not in st.session_state: st.session_state.language = "English"
if "visits" not in st.session_state: st.session_state.visits = 0
if "conversions" not in st.session_state: st.session_state.conversions = 0
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "recommended_program" not in st.session_state: st.session_state.recommended_program = ""
if "match_score" not in st.session_state: st.session_state.match_score = 0

st.session_state.visits += 1

# -------------------------------------------------------------------------------------
# LOAD DATA
# -------------------------------------------------------------------------------------
with open("faqs.json", "r", encoding="utf-8") as f:
    FAQS = json.load(f)

# -------------------------------------------------------------------------------------
# CUSTOM CSS
# -------------------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Lato:wght@300;400;700&display=swap');

:root {
    --primary: #881337;
    --gold: #fbbf24;
    --glass: rgba(255, 255, 255, 0.75);
    --pink: #fb7185;
}

.stApp {
    background: linear-gradient(120deg, #fdf2f8, #fce7f3, #fff1f2);
    font-family: 'Lato', sans-serif;
}

h1, h2, h3, .big-font {
    font-family: 'Playfair Display', serif;
    color: var(--primary);
}

.glass-card {
    background: var(--glass);
    backdrop-filter: blur(12px);
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.6);
    padding: 2rem;
    box-shadow: 0 8px 32px rgba(136, 19, 55, 0.05);
    margin-bottom: 1.5rem;
    transition: all 0.3s ease;
}
.glass-card:hover { 
    transform: translateY(-5px); 
    border-color: #f472b6;
    box-shadow: 0 12px 40px rgba(136, 19, 55, 0.1);
}

.stButton > button {
    background: linear-gradient(to right, #be123c, #fb7185);
    color: white;
    border-radius: 30px;
    border: none;
    padding: 12px 28px;
    font-weight: bold;
    letter-spacing: 1px;
    box-shadow: 0 4px 14px rgba(190, 18, 60, 0.4);
    transition: all 0.3s ease;
}
.stButton > button:hover {
    box-shadow: 0 6px 20px rgba(190, 18, 60, 0.6);
    transform: scale(1.05);
}

.progress-container {
    background: rgba(255,255,255,0.8);
    border-radius: 15px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}
.progress-bar {
    height: 12px;
    background: linear-gradient(to right, #fbbf24, #f59e0b);
    border-radius: 10px;
    transition: width 0.5s ease;
    box-shadow: 0 2px 8px rgba(251, 191, 36, 0.3);
}

.match-score {
    background: linear-gradient(135deg, #fff, #fef3c7);
    border-radius: 50%;
    width: 140px;
    height: 140px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2.5rem;
    border: 6px solid #fb7185;
    margin: auto;
    font-weight: bold;
    color: var(--primary);
    box-shadow: 0 8px 24px rgba(251, 113, 133, 0.3);
}

.success-story {
    background: linear-gradient(135deg, #fef3c7, #fde68a);
    padding: 1.5rem;
    border-radius: 15px;
    border-left: 5px solid var(--gold);
    margin: 1rem 0;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.stat-box {
    background: white;
    padding: 1.5rem;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    border: 2px solid #fce7f3;
}

.chat-message {
    background: white;
    padding: 1rem;
    border-radius: 15px;
    margin: 0.5rem 0;
    border-left: 4px solid var(--pink);
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.welcome-banner {
    background: linear-gradient(135deg, #881337, #be123c);
    color: white;
    padding: 2rem;
    border-radius: 20px;
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 8px 24px rgba(136, 19, 55, 0.3);
}

.feature-badge {
    display: inline-block;
    background: var(--gold);
    color: var(--primary);
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-weight: bold;
    margin: 0.25rem;
    font-size: 0.9rem;
}

.comparison-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    margin: 1rem 0;
}
.comparison-table th {
    background: var(--primary);
    color: white;
    padding: 1rem;
    text-align: left;
}
.comparison-table td {
    background: white;
    padding: 1rem;
    border-bottom: 1px solid #fce7f3;
}
.comparison-table tr:hover td {
    background: #fef3c7;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------------------------
# HEADER
# -------------------------------------------------------------------------------------
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.markdown("# 👑 Iron Lady Navigator")
    st.markdown("### AI-Powered Leadership Path Designer")
with col2:
    st.image("https://cdn-icons-png.flaticon.com/512/6997/6997662.png", width=90)
with col3:
    st.selectbox("🌐 Language", config.LANGUAGES.keys(), key="lang_select",
                 on_change=lambda: setattr(st.session_state, "language", st.session_state.lang_select))

# -------------------------------------------------------------------------------------
# STAGE 0: WELCOME & DATA COLLECTION
# -------------------------------------------------------------------------------------
if st.session_state.stage == 0:
    
    # Welcome Banner
    st.markdown("""
    <div class="welcome-banner">
        <h2>🎯 Transform Your Leadership Journey in 3 Minutes</h2>
        <p style="font-size:1.1rem; margin-top:1rem;">
            Asha, your AI Leadership Architect, will analyze your profile and design a personalized roadmap to success.
        </p>
        <div style="margin-top:1.5rem;">
            <span class="feature-badge">🤖 AI-Powered</span>
            <span class="feature-badge">🌍 Multi-Language</span>
            <span class="feature-badge">📊 92% Success Rate</span>
            <span class="feature-badge">⚡ Instant Results</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Main Form
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🌸 Tell Asha About Yourself")

    col_a, col_b = st.columns(2)
    with col_a:
        name = st.text_input("👩 Your Name", placeholder="Anjali Sharma")
        role = st.selectbox("📊 Current Stage", ["Student", "Professional", "Manager", "Career Break", "Entrepreneur"])
    with col_b:
        challenge = st.selectbox("⚠️ Biggest Challenge", 
                                 ["Low Confidence", "Stagnant Career", "Return to Work", "Public Speaking", 
                                  "Work-Life Balance", "Leadership Skills"])
        goal = st.text_area("🎯 Your 6-Month Goal", 
                           placeholder="I want to become a confident team leader and get promoted to senior management...", 
                           height=100)

    st.markdown('</div>', unsafe_allow_html=True)

     # CTA Button
    if st.button("✨ Get My Free AI-Powered Roadmap", use_container_width=True):
        if goal and name:
            st.session_state.user_data = {
                "name": name, 
                "role": role, 
                "challenge": challenge, 
                "goal": goal,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state.stage = 1
            st.session_state.progress = 50
            st.rerun()
        else:
            st.warning("⚠️ Please fill in your name and goal to continue.")

    # Success Stories Preview
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🌟 Real Transformation Stories")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="success-story">
            <strong>Priya M. - Software Engineer</strong><br>
            "From coding silently to leading a team of 12 in 6 months!"<br>
            <small>📍 Bangalore • Leadership Accelerator</small>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="success-story">
            <strong>Sneha K. - Career Break (5 yrs)</strong><br>
            "Landed Senior Manager role after restart program!"<br>
            <small>📍 Mumbai • Career Restart Launchpad</small>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="success-story">
            <strong>Anita R. - Entrepreneur</strong><br>
            "Scaled my startup from 2 to 45 employees with confidence!"<br>
            <small>📍 Delhi • 10X Masterclass</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

   

# -------------------------------------------------------------------------------------
# STAGE 1: AI RECOMMENDATION & ENGAGEMENT
# -------------------------------------------------------------------------------------
elif st.session_state.stage == 1:

    # Sidebar Analytics
    with st.sidebar:
        st.markdown("### 📊 Live Analytics Dashboard")
        st.metric("Total Visits Today", st.session_state.visits)
        st.metric("Conversions", st.session_state.conversions)
        conversion_rate = (st.session_state.conversions / st.session_state.visits * 100) if st.session_state.visits > 0 else 0
        st.metric("Conversion Rate", f"{conversion_rate:.1f}%")
        
        st.markdown("---")
        st.markdown("### 🧪 A/B Test Control")
        old_version = st.session_state.ab_test_version
        st.session_state.ab_test_version = st.radio(
            "Version", ["A", "B"], 
            index=0 if st.session_state.ab_test_version == "A" else 1,
            help="A: Warm mentoring | B: Urgent FOMO"
        )
        if old_version != st.session_state.ab_test_version:
            st.session_state.ai_response = ""  # Reset to regenerate
            st.rerun()

    # Generate AI Recommendation (Once)
    # Generate AI Recommendation (Once)
    if st.session_state.ai_response == "":
        
        # RATE LIMITING
        if "last_call" in st.session_state and time.time() - st.session_state.last_call < 5:
            st.warning("⏳ Please wait a few seconds before generating again...")
            st.stop()
            
        st.session_state.last_call = time.time()

        with st.spinner("✨ Asha is analyzing your profile and designing your roadmap..."):
            time.sleep(1.5)  # Dramatic effect
            
            # Use cached function
            st.session_state.ai_response = generate_roadmap(
                st.session_state.user_data, 
                st.session_state.ab_test_version, 
                st.session_state.language
            )
            
            # Extract match score
            st.session_state.match_score = calculate_match_score(st.session_state.ai_response)
            
            # Extract recommended program
            for prog in config.PROGRAMS_DB.keys():
                if prog.lower() in st.session_state.ai_response.lower():
                    st.session_state.recommended_program = prog
                    break
            
            # Save Lead
            st.session_state.user_data['program'] = st.session_state.recommended_program
            save_lead(st.session_state.user_data)

    # Progress Tracker
    st.markdown('<div class="progress-container">', unsafe_allow_html=True)
    st.markdown(f"""
    ### 📈 Your Leadership Journey Progress
    <div style="display:flex; gap:20px; align-items:center;">
        <div style="flex:1;">
            <div class="progress-bar" style="width:{st.session_state.progress}%;"></div>
        </div>
        <span style="color:#881337; font-weight:bold;">{st.session_state.progress}% Complete</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Main AI Roadmap
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(f"## 🎉 {st.session_state.user_data['name']}'s Personalized Leadership Roadmap")
    st.markdown(st.session_state.ai_response)
    st.markdown('</div>', unsafe_allow_html=True)

    # Match Score & Quick Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🔥 AI Match Score")
        st.markdown(f'<div class="match-score">{st.session_state.match_score}%</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.markdown("### 📚 Best Fit")
        st.markdown(f"**{st.session_state.recommended_program or 'Leadership Accelerator'}**")
        st.markdown("6 Months • Live Sessions")
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.markdown("### 🎯 Success Rate")
        st.markdown("**89%**")
        st.markdown("Women achieved their goals")
        st.markdown('</div>', unsafe_allow_html=True)

    # Download Roadmap
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 📥 Save Your Roadmap")
    
    roadmap_text = f"""
IRON LADY - PERSONALIZED LEADERSHIP ROADMAP
Generated: {st.session_state.user_data['timestamp']}

PROFILE:
Name: {st.session_state.user_data['name']}
Stage: {st.session_state.user_data['role']}
Challenge: {st.session_state.user_data['challenge']}
Goal: {st.session_state.user_data['goal']}

AI MATCH SCORE: {st.session_state.match_score}%

{st.session_state.ai_response}

---
Next Steps: WhatsApp +91 98765 43210 to speak with a counselor
Website: www.iamironlady.com
"""
    
    st.download_button(
        label="📄 Download as TXT",
        data=roadmap_text,
        file_name=f"IronLady_Roadmap_{st.session_state.user_data['name'].replace(' ', '_')}.txt",
        mime="text/plain",
        use_container_width=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # FAQs Integration
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### ❓ Quick Answers to Common Questions")
    
    faq_tab1, faq_tab2 = st.tabs(["📋 All FAQs", "🔍 Search"])
    
    with faq_tab1:
        for i, faq in enumerate(FAQS):
            with st.expander(f"**{faq['question']}**"):
                st.markdown(faq['answer'])
    
    with faq_tab2:
        search_term = st.text_input("🔍 Search FAQs", placeholder="e.g., EMI, certificate, online...")
        if search_term:
            results = [faq for faq in FAQS if search_term.lower() in faq['question'].lower() or search_term.lower() in faq['answer'].lower()]
            if results:
                for faq in results:
                    st.markdown(f"**Q: {faq['question']}**")
                    st.markdown(faq['answer'])
                    st.markdown("---")
            else:
                st.info("No FAQs found. Try different keywords or ask Asha below!")
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Interactive Follow-up Chat
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 💬 Ask Asha Anything")
    st.markdown("*Have questions about the program, schedule, or your roadmap? Ask away!*")
    
    user_question = st.text_input("Your question:", placeholder="E.g., Can I join if I work full-time?", key="followup_q")
    
    if st.button("💡 Get Answer", use_container_width=True):
        if user_question:
            try:
                client = Groq(api_key=os.getenv("GROQ_API_KEY"))
                
                followup_prompt = f"""
You are Asha, Iron Lady's AI mentor. The user asked: "{user_question}"

Context:
- User: {st.session_state.user_data['name']}
- Recommended Program: {st.session_state.recommended_program}
- Their Goal: {st.session_state.user_data['goal']}

Answer warmly and specifically. If it's about logistics, be factual. If it's about confidence, be motivating.
Language: {config.LANGUAGES[st.session_state.language]["name"]}
"""
                
                with st.spinner("Asha is thinking..."):
                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "user", "content": followup_prompt}],
                        temperature=0.6,
                        max_tokens=400
                    )
                    answer = response.choices[0].message.content
                    
                    st.session_state.chat_history.append({"q": user_question, "a": answer})
                    
            except Exception as e:
                st.error("Couldn't reach Asha right now. Please try WhatsApp support below.")
    
    # Display chat history
    if st.session_state.chat_history:
        st.markdown("#### 💬 Conversation History")
        for chat in st.session_state.chat_history[-3:]:  # Show last 3
            st.markdown(f'<div class="chat-message"><strong>You:</strong> {chat["q"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="chat-message" style="border-left-color:#fbbf24;"><strong>Asha:</strong> {chat["a"]}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Payment CTA
    st.markdown('<div class="glass-card" style="background: linear-gradient(135deg, #fef3c7, #fde68a);">', unsafe_allow_html=True)
    st.markdown("### 💳 Limited Time Offer - Enroll Now!")
    
    col_p1, col_p2 = st.columns([2, 1])
    with col_p1:
        discount_text = "⚡ FLASH SALE - 72% OFF!" if st.session_state.ab_test_version == "B" else "🎁 Special Offer - 70% OFF"
        st.markdown(f"""
        **{discount_text}**  
        {st.session_state.recommended_program or 'Leadership Accelerator'}  
        ~~₹99,997~~ → **₹29,997**
        
        ✅ Live Sessions • ✅ Mentorship • ✅ Certificate • ✅ Community Access
        """)
        
        if st.session_state.ab_test_version == "B":
            st.markdown("⚠️ **Only 3 seats left at this price!**")
    
    with col_p2:
        if st.button("🛒 Enroll Now - ₹29,997", use_container_width=True, type="primary"):
            st.session_state.conversions += 1
            st.balloons()
            st.success("🎉 Welcome to Iron Lady! Check your email for next steps.")
            st.info("📞 Our counselor will call you in 10 minutes to complete enrollment.")
    
    st.markdown('</div>', unsafe_allow_html=True)

    # WhatsApp CTA
    wa_link = get_whatsapp_link(st.session_state.user_data['name'], st.session_state.recommended_program)
    
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#25D366,#128C7E); 
                padding:30px; border-radius:25px; color:white; text-align:center; margin-top:30px;">
        <h2>📞 Speak to a Real Mentor in 60 Seconds</h2>
        <p style="font-size:1.2rem;"><strong>Get Your Questions Answered LIVE</strong></p>
        <a href="{wa_link}" target="_blank" style="
            background:#fbbf24; padding:18px 50px; border-radius:50px; 
            color:#881337; font-size:1.3rem; text-decoration:none; font-weight:700;
            display:inline-block; margin-top:15px;">
            💬 WhatsApp Asha Now (FREE)
        </a>
        <p style="margin-top:15px; font-size:0.9rem;">⚡ Avg. response time: 2 minutes</p>
    </div>
    """, unsafe_allow_html=True)

    # Social Sharing
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🌟 Share Your Roadmap")
    
    share_text = generate_share_text(st.session_state.user_data['name'], st.session_state.match_score)
    
    col_s1, col_s2, col_s3 = st.columns(3)
    
    # Pre-process text for different platforms
    import urllib.parse
    
    # 1. LinkedIn (Feed Share)
    # LinkedIn's web app often crashes (URIError) if it tries to decode a '%' symbol
    # that has been decoded once already (double-decode issue).
    # To be safe, we replace the literal '%' in the user's text with ' percent'.
    linkedin_safe_text = share_text.replace("%", " percent")
    full_linkedin_text = f"{linkedin_safe_text} https://iamironlady.com"
    
    # We use quote instead of urlencode to force %20 for spaces instead of +, 
    # which is generally safer for these strict parsers.
    encoded_linkedin_text = urllib.parse.quote(full_linkedin_text)
    
    linkedin_url = f"https://www.linkedin.com/feed/?shareActive=true&text={encoded_linkedin_text}"
    
    # 2. Twitter
    twitter_params = {
        "text": share_text,
        "url": "https://iamironlady.com"
    }
    twitter_url = f"https://twitter.com/intent/tweet?{urllib.parse.urlencode(twitter_params)}"
    
    # 3. Clipboard (JavaScript)
    # Escape single quotes for JS string: ' -> \'
    js_safe_text = share_text.replace("'", "\\'")
    
    with col_s1:
        st.markdown(f'<a href="{linkedin_url}" target="_blank"><button style="background:#0077b5; color:white; padding:10px 20px; border:none; border-radius:10px; cursor:pointer; width:100%;">📘 Share on LinkedIn</button></a>', unsafe_allow_html=True)
    with col_s2:
        st.markdown(f'<a href="{twitter_url}" target="_blank"><button style="background:#1DA1F2; color:white; padding:10px 20px; border:none; border-radius:10px; cursor:pointer; width:100%;">🐦 Share on Twitter</button></a>', unsafe_allow_html=True)
    with col_s3:
        st.markdown(f'<button onclick="navigator.clipboard.writeText(\'{js_safe_text} https://iamironlady.com\')" style="background:#fb7185; color:white; padding:10px 20px; border:none; border-radius:10px; cursor:pointer; width:100%;">📋 Copy Text</button>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Reset Button
    if st.button("🔄 Start New Assessment", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key not in ['visits', 'conversions']:
                del st.session_state[key]
        st.rerun()

# -------------------------------------------------------------------------------------
# FOOTER
# -------------------------------------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#881337; padding:2rem;">
    <strong>Iron Lady - Empowering Women Leaders Since 2019</strong><br>
    🌐 www.iamironlady.com | 📧 hello@iamironlady.com | 📞 +91 98765 43210<br>
    <small>Powered by AI • Built with ❤️ for Women Who Lead</small>
</div>
""", unsafe_allow_html=True)