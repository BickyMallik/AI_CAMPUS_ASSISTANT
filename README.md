# 🎓 AI Campus Assistant

> AI-powered grievance and feedback portal for college students.

---

## 📁 Project Structure
```
AI_CAMPUS_ASSISTANT/
├── backend/
│   ├── main.py          # FastAPI routes
│   ├── ai_service.py    # Groq AI integration
│   ├── database.py      # MySQL connection & init
│   ├── models.py        # Pydantic schemas
│   ├── requirements.txt
│   └── .env.example     # ← Copy to .env and fill in
├── frontend/
│   ├── index.html       # Student portal
│   ├── admin.html       # Admin dashboard
│   ├── style.css
│   └── script.js
└── render.yaml          # Render deployment config
```

---

## ⚡ Local Setup (Step-by-Step)

### Step 1 — Prerequisites
- Python 3.10+
- MySQL running locally
- VS Code

### Step 2 — Clone and setup
```bash
cd backend
pip install -r requirements.txt
```

### Step 3 — Create `.env` file
```bash
# In backend/ folder
cp .env.example .env
# Now edit .env with your MySQL credentials
```

### Step 4 — Get FREE Groq API Key (2 minutes)
1. Go to https://console.groq.com
2. Sign up (no credit card required)
3. Click "API Keys" → "Create API Key"
4. Paste the key in `.env` as `GROQ_API_KEY=gsk_...`

### Step 5 — Start the server
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### Step 6 — Open the app
- **Student Portal**: Open `frontend/index.html` in browser  
  *OR* visit http://localhost:8000
- **Admin Panel**: Open `frontend/admin.html`  
  Default credentials: `admin` / `admin123`
- **Swagger API Docs**: http://localhost:8000/docs

---

## 🤖 AI Provider — Why Groq?

| Provider | Free Tier | Quota Issue | Speed |
|----------|-----------|-------------|-------|
| Gemini   | ❌ 0 requests (your issue) | Yes | Fast |
| OpenAI   | ❌ Requires payment | Sometimes | Fast |
| **Groq** | ✅ 14,400 req/day free | No | Ultra-fast |
| Ollama   | ✅ Fully local | No | Slow on CPU |

**Groq Llama 3** gives 14,400 free requests/day — perfect for demos.

---

## 🌐 Deployment on Render

1. Push code to GitHub
2. Go to https://render.com → New Web Service
3. Connect your GitHub repo
4. Set environment variables in Render dashboard:
   - `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
   - `GROQ_API_KEY`
   - `ADMIN_PASSWORD`
5. Deploy!

> For MySQL on Render: Use PlanetScale (free MySQL cloud) at https://planetscale.com

---

## 🔑 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/grievance/submit` | Submit new grievance |
| GET | `/api/grievance/track/{roll}` | Track by roll number |
| POST | `/api/chat` | AI chatbot |
| POST | `/api/admin/login` | Admin login |
| GET | `/api/admin/grievances` | All grievances |
| PUT | `/api/admin/grievances/{id}/status` | Update status |
| GET | `/api/admin/stats` | Dashboard stats |
| DELETE | `/api/admin/grievances/{id}` | Delete grievance |

---

## 🛡️ Fallback Mode
If Groq API key is not set, the chatbot uses **rule-based responses** for common queries (attendance, hostel, fees, exams, library, WiFi). This ensures the app never crashes during a demo.

---

## 👨‍💻 Built With
- Python FastAPI
- Groq API (Llama 3)
- MySQL
- Vanilla HTML/CSS/JS (Tailwind-inspired custom CSS)
- Deployable on Render
