import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     int(os.getenv("DB_PORT", 3306)),
    "user":     os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "campus_assistant"),
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def init_db():
    config_no_db = {k: v for k, v in DB_CONFIG.items() if k != "database"}
    conn = mysql.connector.connect(**config_no_db)
    cursor = conn.cursor()
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.execute(f"USE {DB_CONFIG['database']}")

        # ── Admins table (one per college) ────────────────────────────────────
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id            INT AUTO_INCREMENT PRIMARY KEY,
                college_name  VARCHAR(200) NOT NULL,
                email         VARCHAR(120) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                college_slug  VARCHAR(100) NOT NULL UNIQUE,
                created_at    DATETIME     NOT NULL
            )
        """)

        # ── Grievances table with college_id ──────────────────────────────────
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS grievances (
                id            INT AUTO_INCREMENT PRIMARY KEY,
                college_id    INT          NOT NULL,
                student_name  VARCHAR(100) NOT NULL,
                student_roll  VARCHAR(30)  NOT NULL,
                department    VARCHAR(80)  NOT NULL,
                category      VARCHAR(50)  NOT NULL,
                subject       VARCHAR(200) NOT NULL,
                description   TEXT         NOT NULL,
                contact_email VARCHAR(120),
                status        ENUM('Pending','In Progress','Resolved','Rejected') DEFAULT 'Pending',
                admin_remarks TEXT,
                submitted_at  DATETIME     NOT NULL,
                updated_at    DATETIME,
                FOREIGN KEY (college_id) REFERENCES admins(id)
            )
        """)

        conn.commit()
        print("✅ Database initialised successfully.")
    finally:
        cursor.close()
        conn.close()
