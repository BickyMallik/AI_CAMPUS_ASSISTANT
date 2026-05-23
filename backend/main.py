from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os, hashlib, re
from datetime import datetime

from database import get_db_connection, init_db
from ai_service import get_ai_response

app = FastAPI(
    title="AI Campus Assistant",
    description="AI-powered grievance and feedback portal for college students",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/frontend", StaticFiles(directory="../frontend", html=True), name="frontend")

@app.on_event("startup")
async def startup():
    init_db()

# ─── Helpers ─────────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def make_slug(college_name: str) -> str:
    slug = re.sub(r'[^a-zA-Z0-9\s]', '', college_name)
    slug = re.sub(r'\s+', '-', slug.strip()).upper()
    return slug

# ─── Models ──────────────────────────────────────────────────────────────────

class GrievanceRequest(BaseModel):
    college_slug:  str
    student_name:  str
    student_roll:  str
    department:    str
    category:      str
    subject:       str
    description:   str
    contact_email: Optional[str] = None

class ChatRequest(BaseModel):
    message:    str
    session_id: Optional[str] = None

class AdminSignup(BaseModel):
    college_name: str
    email:        str
    password:     str

class AdminLogin(BaseModel):
    email:    str
    password: str

class StatusUpdate(BaseModel):
    status:        str
    admin_remarks: Optional[str] = None

# ─── Student Endpoints ────────────────────────────────────────────────────────

@app.get("/")
def root():
    return FileResponse("../frontend/index.html")

@app.get("/api/college/{slug}")
def get_college_info(slug: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id, college_name, college_slug FROM admins WHERE college_slug = %s",
            (slug.upper(),)
        )
        college = cursor.fetchone()
        if not college:
            raise HTTPException(status_code=404, detail="College not found")
        return {"success": True, "college": college}
    finally:
        cursor.close()
        conn.close()

@app.post("/api/grievance/submit")
def submit_grievance(req: GrievanceRequest):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Get college id from slug
        cursor.execute(
            "SELECT id FROM admins WHERE college_slug = %s",
            (req.college_slug.upper(),)
        )
        college = cursor.fetchone()
        if not college:
            raise HTTPException(status_code=404, detail="Invalid college. Please use the correct portal link.")

        cursor.execute("""
            INSERT INTO grievances
            (college_id, student_name, student_roll, department, category, subject, description, contact_email, status, submitted_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Pending', %s)
        """, (
            college["id"], req.student_name, req.student_roll, req.department,
            req.category, req.subject, req.description,
            req.contact_email, datetime.now()
        ))
        conn.commit()
        grievance_id = cursor.lastrowid
        return {
            "success": True,
            "message": "Grievance submitted successfully!",
            "grievance_id": grievance_id,
            "ticket": f"TICKET-{grievance_id:04d}"
        }
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.get("/api/grievance/track/{college_slug}/{roll_number}")
def track_grievance(college_slug: str, roll_number: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM admins WHERE college_slug = %s", (college_slug.upper(),))
        college = cursor.fetchone()
        if not college:
            raise HTTPException(status_code=404, detail="Invalid college.")

        cursor.execute("""
            SELECT id, subject, category, status, submitted_at, admin_remarks
            FROM grievances
            WHERE student_roll = %s AND college_id = %s
            ORDER BY submitted_at DESC
        """, (roll_number, college["id"]))
        grievances = cursor.fetchall()
        if not grievances:
            raise HTTPException(status_code=404, detail="No grievances found for this roll number.")
        return {"success": True, "grievances": grievances}
    finally:
        cursor.close()
        conn.close()

@app.post("/api/chat")
async def chat_with_ai(req: ChatRequest):
    try:
        response = await get_ai_response(req.message)
        return {"success": True, "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

# ─── Admin Auth Endpoints ─────────────────────────────────────────────────────

@app.post("/api/admin/signup")
def admin_signup(req: AdminSignup):
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Check email already exists
        cursor.execute("SELECT id FROM admins WHERE email = %s", (req.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered.")

        slug = make_slug(req.college_name)

        # Check slug already exists
        cursor.execute("SELECT id FROM admins WHERE college_slug = %s", (slug,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="A college with a similar name already exists.")

        password_hash = hash_password(req.password)
        cursor.execute("""
            INSERT INTO admins (college_name, email, password_hash, college_slug, created_at)
            VALUES (%s, %s, %s, %s, %s)
        """, (req.college_name, req.email, password_hash, slug, datetime.now()))
        conn.commit()

        return {
            "success": True,
            "message": "Account created successfully!",
            "college_slug": slug,
            "portal_link": f"?college={slug}",
            "admin_link": f"admin.html?college={slug}"
        }
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/api/admin/login")
def admin_login(req: AdminLogin):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        password_hash = hash_password(req.password)
        cursor.execute(
            "SELECT id, college_name, college_slug FROM admins WHERE email = %s AND password_hash = %s",
            (req.email, password_hash)
        )
        admin = cursor.fetchone()
        if not admin:
            raise HTTPException(status_code=401, detail="Invalid email or password.")
        return {
            "success": True,
            "message": "Login successful",
            "college_name": admin["college_name"],
            "college_slug": admin["college_slug"],
            "admin_id": admin["id"]
        }
    finally:
        cursor.close()
        conn.close()

# ─── Admin Dashboard Endpoints ────────────────────────────────────────────────

@app.get("/api/admin/grievances")
def get_all_grievances(college_slug: str, status: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM admins WHERE college_slug = %s", (college_slug.upper(),))
        college = cursor.fetchone()
        if not college:
            raise HTTPException(status_code=404, detail="College not found.")

        if status and status != "All":
            cursor.execute(
                "SELECT * FROM grievances WHERE college_id = %s AND status = %s ORDER BY submitted_at DESC",
                (college["id"], status)
            )
        else:
            cursor.execute(
                "SELECT * FROM grievances WHERE college_id = %s ORDER BY submitted_at DESC",
                (college["id"],)
            )
        grievances = cursor.fetchall()
        return {"success": True, "grievances": grievances, "total": len(grievances)}
    finally:
        cursor.close()
        conn.close()

@app.get("/api/admin/stats")
def get_stats(college_slug: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM admins WHERE college_slug = %s", (college_slug.upper(),))
        college = cursor.fetchone()
        if not college:
            raise HTTPException(status_code=404, detail="College not found.")

        cid = college["id"]
        cursor.execute("SELECT COUNT(*) as total FROM grievances WHERE college_id = %s", (cid,))
        total = cursor.fetchone()["total"]

        cursor.execute(
            "SELECT status, COUNT(*) as count FROM grievances WHERE college_id = %s GROUP BY status",
            (cid,)
        )
        by_status = cursor.fetchall()

        cursor.execute(
            "SELECT category, COUNT(*) as count FROM grievances WHERE college_id = %s GROUP BY category ORDER BY count DESC LIMIT 5",
            (cid,)
        )
        by_category = cursor.fetchall()

        cursor.execute("""
            SELECT DATE_FORMAT(submitted_at, '%b') as month, COUNT(*) as count
            FROM grievances WHERE college_id = %s
            GROUP BY month ORDER BY submitted_at ASC LIMIT 6
        """, (cid,))
        by_month = cursor.fetchall()

        return {
            "total": total,
            "by_status": by_status,
            "by_category": by_category,
            "by_month": by_month
        }
    finally:
        cursor.close()
        conn.close()

@app.put("/api/admin/grievances/{grievance_id}/status")
def update_grievance_status(grievance_id: int, update: StatusUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE grievances SET status = %s, admin_remarks = %s, updated_at = %s WHERE id = %s",
            (update.status, update.admin_remarks, datetime.now(), grievance_id)
        )
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Grievance not found")
        return {"success": True, "message": "Status updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.delete("/api/admin/grievances/{grievance_id}")
def delete_grievance(grievance_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM grievances WHERE id = %s", (grievance_id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Grievance not found")
        return {"success": True, "message": "Grievance deleted"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
