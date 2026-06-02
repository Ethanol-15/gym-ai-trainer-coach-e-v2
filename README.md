# 🏋️ Coach E — AI-Powered Personal Gym Coach

An AI-powered fitness coaching web application built using LLaMA 3.3, Retrieval Augmented Generation (RAG), Supabase, and Streamlit.

Coach E combines conversational AI with real-world fitness tracking systems including calorie tracking, weight tracking, strength progression analytics, authentication, and persistent chat history.

🔗 **Live Demo:** https://coach-e-gym.streamlit.app

---

# 🚀 Features

### 🤖 AI Gym Coach
- Powered by **LLaMA 3.3 70B** via Groq API
- Personalized hypertrophy and nutrition coaching
- Maintains conversation memory and coaching context
- Uses Retrieval Augmented Generation (RAG) with a custom fitness dataset

### 🧠 Retrieval Augmented Generation (RAG)
- Searches a custom 450+ entry hypertrophy knowledge base
- Uses FAISS vector similarity search
- SentenceTransformers embedding pipeline
- Grounds AI responses in evidence-based training information

### 🔐 Authentication System
- User login and signup system
- Persistent user sessions
- Guest mode with free chat limitations
- User-specific data storage using Supabase

### 💬 Persistent Conversation History
- Conversations saved to Supabase database
- Chat threads stored per user account
- Delete conversations functionality
- Multi-conversation sidebar system similar to ChatGPT

### ⚖️ Weight Tracker
- Daily bodyweight logging
- Progress line graph visualization
- Weight analytics:
  - highest weight
  - lowest weight
  - total weight change
  - trend analysis

### 💪 Strength Tracker
- Supports:
  - Gym exercises
  - Calisthenics
  - Weighted calisthenics
- Tracks:
  - sets
  - reps
  - weight used
  - bodyweight
- Calculates estimated strength progression using the Epley formula
- Exercise-specific progress graphs and analytics

### 🍽️ Calorie & Macro Tracker
- User-defined calorie and macro goals
- Daily nutrition logging
- Tracks:
  - calories
  - protein
  - carbs
  - fats
- Displays remaining macros and calories for the day
- Nutrition analytics dashboard

### 📊 Analytics Dashboard
- Interactive Plotly graphs
- Progress trend visualization
- User-specific tracking analytics
- Real-time progress monitoring

---

# 🧠 How It Works

```text
User asks a question
        ↓
RAG searches custom fitness knowledge base
        ↓
Top relevant entries retrieved using FAISS
        ↓
System prompt + RAG context + chat history
sent to Groq API
        ↓
LLaMA 3.3 generates grounded coaching response
        ↓
Conversation + tracker data saved to Supabase
```

---

# 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core backend/application logic |
| Streamlit | Frontend web framework |
| Supabase | Cloud database + authentication |
| LLaMA 3.3 70B | Large language model |
| Groq API | Ultra-fast LLM inference |
| RAG | Retrieval Augmented Generation |
| FAISS | Vector similarity search |
| SentenceTransformers | Embedding generation |
| Plotly | Interactive analytics charts |
| Pandas | Data analysis |
| GitHub | Version control |
| Streamlit Cloud | Deployment platform |

---

# 🏗️ Architecture

## AI Pipeline

```text
User Prompt
    ↓
RAG Retrieval
    ↓
FAISS Similarity Search
    ↓
Relevant Knowledge Base Entries
    ↓
System Prompt + Memory + RAG Context
    ↓
Groq API (LLaMA 3.3)
    ↓
AI Response
```

---

## Backend Architecture

```text
Frontend (Streamlit)
        ↓
Application Logic (Python)
        ↓
Supabase Backend
        ↓
Tables:
- users
- conversations
- messages
- weight_logs
- strength_logs
- calorie_logs
- calorie_goals
```

---

# 📁 Project Structure

```text
gym-ai-trainer-coach-e-v2/
│
├── app.py
├── rag.py
├── auth.py
├── sidebar.py
├── prompts.py
├── weight_tracker.py
├── strength_tracker.py
├── calorie_tracker.py
├── gym_data.json
├── requirements.txt
├── .gitignore
└── README.md
```

---

# 📊 Database Features

## Supabase Tables

### users
Stores user authentication data

### conversations
Stores user chat sessions

### messages
Stores AI and user chat messages

### weight_logs
Stores bodyweight tracking data

### strength_logs
Stores exercise progression data

### calorie_logs
Stores daily calorie and macro intake

### calorie_goals
Stores nutrition goals

---

# 🏋️ Coaching Philosophy

Coach E follows an evidence-based hypertrophy philosophy focused on:

- High intensity low volume training
- Mechanical tension
- Progressive overload
- Stable exercise selection
- Machine and cable preference
- Nutrition tracking
- Recovery optimization

---

# ⚙️ Installation

## Prerequisites
- Python 3.10+
- Groq API key
- Supabase project

## Local Setup

```bash
git clone https://github.com/Ethanol-15/gym-ai-trainer-coach-e-v2.git

cd gym-ai-trainer-coach-e-v2

pip install -r requirements.txt

streamlit run app.py
```

---

# 🔑 Environment Variables

Add to `.streamlit/secrets.toml`

```toml
GROQ_API_KEY = "your_groq_api_key"

SUPABASE_URL = "your_supabase_url"

SUPABASE_KEY = "your_supabase_anon_key"
```

---

# 🧪 Engineering Concepts Used

- Retrieval Augmented Generation (RAG)
- Vector embeddings
- Similarity search
- Prompt engineering
- Session state management
- Database schema design
- Authentication systems
- Analytics pipelines
- Full-stack AI application architecture

---

# 🛣️ Roadmap

- [x] Authentication system
- [x] Persistent conversations
- [x] Weight tracker
- [x] Strength tracker
- [x] Calorie tracker
- [x] Supabase migration
- [x] Analytics dashboards
- [ ] Exercise recommendation engine
- [ ] AI-generated workout plans
- [ ] Streaming AI responses
- [ ] Voice input integration
- [ ] Mobile optimization
- [ ] Wearable integration

---

# 👤 Author

## Ethan Lyle Cruz

- GitHub: https://github.com/Ethanol-15
- LinkedIn: https://www.linkedin.com/in/ethan-cruz-992730337/

---

# 📄 License

MIT License

---

Built with LLaMA, RAG, Supabase, and an obsession with hyper
