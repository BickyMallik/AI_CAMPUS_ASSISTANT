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

## Step 4 — Get FREE OpenRouter API Key (2 minutes)
1. Go to https://openrouter.ai
2. Sign up with Google (no credit card required)
3. Click "API Keys" → "Create Key"
4. Paste the key in `.env` as `OPENROUTER_API_KEY=sk-or-...`

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

| Provider | Free Tier | Quota Issue | Speed |
|----------|-----------|-------------|-------|
| Gemini | ❌ 0 requests (quota blocked) | Yes | Fast |
| OpenAI | ❌ Requires payment | Sometimes | Fast |
| Groq | ❌ Email signup issues | Sometimes | Fast |
| **OpenRouter** | ✅ Free models, no card | No | Fast |

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
