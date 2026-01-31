# 🏆 Iron Lady AI Navigator - Task 1 Submission

## 🎯 Project Overview

**AI-Powered Customer Journey Solution for Iron Lady**

An intelligent, multi-language leadership path designer that uses AI to analyze user profiles and provide personalized program recommendations, creating an engaging customer experience that drives conversions.

---

## 🚀 Key Features

### ✨ Core Functionality
- **AI-Powered Personalization**: Uses Groq's LLaMA 3.1 model for intelligent recommendations
- **Multi-Language Support**: English, Hindi, Telugu, Tamil
- **Interactive Customer Journey**: Welcome → Profile → AI Analysis → Recommendation → Conversion
- **Real-Time Match Scoring**: AI calculates program fit percentage
- **A/B Testing**: Compare "Warm Mentoring" vs "Urgent FOMO" messaging

### 🎨 User Experience
- **Glass Morphism UI**: Modern, premium design
- **Progress Tracking**: Visual journey completion indicator
- **Success Stories**: Social proof integration
- **FAQ Integration**: Searchable knowledge base
- **Follow-up Chat**: Interactive Q&A with AI mentor
- **Downloadable Roadmap**: Export personalized recommendations

### 💼 Business Intelligence
- **Live Analytics**: Visit tracking, conversion monitoring
- **Conversion Optimization**: Strategic CTAs with offers
- **WhatsApp Integration**: Direct mentor connection
- **Social Sharing**: LinkedIn, Twitter integration
- **Lead Capture**: Structured user data collection

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | Streamlit (Python) |
| **AI/ML** | Groq API (LLaMA 3.1-8b-instant) |
| **Language** | Python 3.9+ |
| **Styling** | Custom CSS (Glass Morphism) |
| **Architecture** | Modular (app.py, config.py, utils.py) |

---

## 📦 Installation & Setup

### Prerequisites
- Python 3.9 or higher
- Groq API key ([Get one free](https://console.groq.com))

### Steps

1. **Clone/Download the project**
```bash
cd iron-lady-task1
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Set environment variable

```bash
# Windows
set GROQ_API_KEY=gsk_...XBzo

# Mac/Linux
export GROQ_API_KEY=your_api_key_here
```

4. Run the application

```bash
streamlit run app.py
```
