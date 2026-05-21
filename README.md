# 🏋️ Coach E — AI-Powered Personal Gym Coach

An AI-powered personal gym coaching web application built with LLaMA 3.3, Retrieval Augmented Generation (RAG), and Streamlit. Coach E provides personalized training and nutrition advice based on evidence-based hypertrophy principles and a high intensity low volume training philosophy.

🔗 **Live Demo:** [coach-e-gym.streamlit.app)

---

## 🚀 Features

- **AI Coaching** — Powered by LLaMA 3.3 70B via Groq API for fast, intelligent responses
- **RAG Architecture** — Searches a custom 450-entry fitness knowledge base before every answer using FAISS vector search
- **Conversation Memory** — Remembers the full context of your conversation for follow-up questions
- **Personalized Philosophy** — Trained on a specific high intensity low volume coaching style
- **Nutrition Guidance** — TDEE calculations, macro setup, calorie tracking advice
- **Program Design** — Full Body, Push Pull Legs, and Upper Lower programs included
- **Free to Use** — Runs entirely on free tier services

---

## 🧠 How It Works

```
User asks a question
        ↓
RAG searches 250 gym knowledge entries
finds top 3 most relevant ones
        ↓
System prompt + RAG context + conversation history
sent to Groq API
        ↓
LLaMA 3.3 70B reads coaching rules first
then generates a personalized response
        ↓
Response displayed in Streamlit chat interface
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| **Python** | Core programming language |
| **LLaMA 3.3 70B** | Large language model for response generation |
| **Groq API** | Ultra-fast LLM inference (free tier) |
| **RAG** | Retrieval Augmented Generation for accurate answers |
| **FAISS** | Vector similarity search for knowledge base |
| **SentenceTransformers** | Text embedding model for RAG |
| **Streamlit** | Web app framework and UI |
| **Streamlit Cloud** | Free deployment platform |
| **GitHub** | Version control and CI/CD |

---

## 📁 Project Structure

```
gym-ai-trainer-coach-e-v2/
│
├── app.py              # Main Streamlit application
├── rag.py              # RAG search system with FAISS
├── gym_data.json       # Custom 450-entry fitness knowledge base
├── requirements.txt    # Python dependencies
├── .gitignore          # Protects API keys and secrets
└── README.md           # Project documentation
```

---

## 🏗️ Architecture

### RAG Pipeline
```
gym_data.json (450 entries)
        ↓
SentenceTransformer embeds all entries into vectors
        ↓
FAISS indexes all vectors for fast similarity search
        ↓
User question → embedded → FAISS finds top 3 matches
        ↓
Matched entries added as context to LLM prompt
        ↓
LLaMA generates response grounded in your knowledge base
```

### Conversation Memory
```
Every message stored in Streamlit session state
Full conversation history sent with each request
Limited to last 10 messages to prevent context overflow
System prompt always preserved at position 0

```

---

## 🏋️ Coaching Philosophy

Coach E is trained on a specific evidence-based training philosophy:

- **High intensity, low volume** — fewer harder sets over more easier sets
- **Mechanical tension focus** — exercises where target muscle fails before stabilizers
- **Machine and cable preference** — more stable, better tension curves
- **Progressive overload** — non-negotiable for every session
- **Calorie tracking** — food scale, no estimation, weekly averages
- **Protein first** — 2.2g per kg bodyweight minimum daily

---

## 📊 Knowledge Base

The custom dataset covers:

- Workout programming (Full Body, PPL 3-day, PPL 6-day, Upper Lower)
- Hypertrophy principles and rep ranges
- Calorie and TDEE calculations
- Macro setup and nutrition planning
- Exercise explanations and preferences
- Plateau breaking strategies
- Supplement recommendations
- Recovery and rest period guidance
- Beginner, intermediate, and advanced programming

---

## ⚙️ Installation

### Prerequisites
- Python 3.10+
- Groq API key (free at [console.groq.com](https://console.groq.com))

### Local Setup

```bash
# Clone the repository
git clone https://github.com/Ethanol-15/gym-ai-trainer-coach-e-v2.git
cd gym-ai-trainer-coach-e-v2

# Install dependencies
pip install -r requirements.txt

# Create secrets file
mkdir .streamlit
echo 'GROQ_API_KEY = "your_key_here"' > .streamlit/secrets.toml

# Run the app
streamlit run app.py
```

---

## 🔑 Environment Variables

| Variable | Description | Where to get it |
|---|---|---|
| `GROQ_API_KEY` | Groq API key for LLM inference | [console.groq.com](https://console.groq.com) |

For local development add to `.streamlit/secrets.toml`:
```toml
GROQ_API_KEY = "your_key_here"
```

For Streamlit Cloud deployment add via the Secrets section in app settings.

---

## 📦 Requirements

```
groq
streamlit
sentence-transformers
faiss-cpu
numpy
```

---

## 🗺️ Roadmap

- [x] RAG with custom fitness knowledge base
- [x] LLaMA 3.3 70B integration via Groq
- [x] Conversation memory
- [x] Streamlit Cloud deployment
- [ ] RAG threshold filtering for better accuracy
- [ ] User profile sidebar for personalized responses
- [ ] Weight tracking integration with database
- [ ] Calorie calculator built in
- [ ] Analytics dashboard for progress tracking
- [ ] FastAPI backend for data persistence
- [ ] User authentication
- [ ] Streaming responses
- [ ] Voice input via Whisper API

---

## 🧪 Background — Built From Scratch

This project started as a learning exercise in building LLMs from scratch:

1. **Transformer architecture** — implemented self-attention, positional encoding, and feed-forward networks from scratch in PyTorch following Raschka (2025) and Vaswani et al. (2017)
2. **GPT-2 fine-tuning** — fine-tuned GPT-2 on a custom gym dataset using LoRA-style training
3. **LLaMA upgrade** — switched to LLaMA 3.3 70B via Groq for production-quality responses
4. **RAG implementation** — built retrieval augmented generation with FAISS for grounded responses

---

## 📚 References

- Raschka, S. (2025). *Build a Large Language Model From Scratch*
- Vaswani et al. (2017). *Attention Is All You Need*
- Meta AI. *LLaMA 3.3*
- Groq. *LPU Inference Engine*

---

## 👤 Author

**Ethan Lyle Cruz**
- GitHub: [@Ethanol-15](https://github.com/Ethanol-15)
- LinkedIN: https://www.linkedin.com/in/ethan-cruz-992730337/


---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

*Built with PyTorch, LLaMA, and a genuine obsession with hypertrophy.*
