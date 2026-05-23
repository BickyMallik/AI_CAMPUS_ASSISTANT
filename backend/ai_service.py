import os
import httpx
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openrouter/free"

SYSTEM_PROMPT = """You are an AI Campus Assistant for a college. Your role is to:
1. Help students with campus-related queries (academic, hostel, canteen, library, admin, fees, exams)
2. Guide students on how to submit grievances through the portal
3. Provide quick, helpful, empathetic responses
4. Suggest solutions before escalating to administration

Categories you handle:
- Academic issues (attendance, marks, course registration, timetable)
- Hostel/accommodation problems (room allotment, maintenance, mess food)
- Library issues (books, access, fines)
- Fees and scholarships
- Examination queries (hall tickets, results, re-evaluation)
- Infrastructure (classrooms, labs, WiFi, electricity)
- Faculty/teaching concerns
- Transportation and bus services
- Medical/health centre queries

Keep responses concise, friendly, and actionable (2-4 sentences max).
If a student should formally file a grievance, tell them to use the Submit Grievance form on this portal.
Always be empathetic — students may be frustrated."""

async def get_ai_response(user_message: str) -> str:
    if not OPENROUTER_API_KEY:
        return get_fallback_response(user_message)

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "AI Campus Assistant",
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_message},
        ],
        "max_tokens": 256,
        "temperature": 0.7,
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(OPENROUTER_API_URL, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            return "I'm receiving too many requests right now. Please try again in a moment."
        return get_fallback_response(user_message)
    except Exception:
        return get_fallback_response(user_message)


def get_fallback_response(message: str) -> str:
    msg = message.lower()
    if any(w in msg for w in ["attendance", "absent", "leave"]):
        return "Attendance issues are handled by your department office. For disputes in recorded attendance, please raise a formal grievance using the form below."
    if any(w in msg for w in ["hostel", "room", "mess", "food", "warden"]):
        return "Hostel-related issues should be first reported to your Hostel Warden. If unresolved within 48 hours, please submit a grievance here."
    if any(w in msg for w in ["fee", "scholarship", "payment"]):
        return "For fee and scholarship queries, visit the Accounts Section. You can also submit a grievance selecting 'Fees & Scholarship' category."
    if any(w in msg for w in ["exam", "result", "marks", "hall ticket"]):
        return "Examination queries are handled by the Examination Cell. For result disputes, submit a grievance selecting 'Examination' category."
    if any(w in msg for w in ["library", "book", "fine"]):
        return "Library issues can be addressed at the Library Counter. For fine waivers, submit a grievance here."
    if any(w in msg for w in ["wifi", "internet", "lab"]):
        return "IT issues should be reported to the IT Helpdesk. For urgent concerns, submit a grievance with category 'Infrastructure'."
    return "Hello! I'm your AI Campus Assistant. I can help with academics, hostel, exams, fees, library and more. How can I assist you today?"