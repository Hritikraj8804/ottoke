import os
import re
import html
import hashlib
from typing import Optional, List
from datetime import datetime, timedelta
import sqlite3
from fastapi import FastAPI, Request, HTTPException, status, Header, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv(".env.local")

app = FastAPI(title="Ottoke API")

# Setup serving for static files (Frontend)
@app.get("/")
def serve_index():
    return FileResponse("frontend/index.html")

@app.get("/submit")
def serve_submit():
    return FileResponse("frontend/submit.html")

@app.get("/leaderboard")
def serve_leaderboard():
    return FileResponse("frontend/leaderboard.html")

@app.get("/icons/{image_name}")
def serve_icon(image_name: str):
    path = f"frontend/icons/{image_name}"
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Icon not found")
    return FileResponse(path)

@app.get("/post/{id}")
def serve_post(id: str):
    return FileResponse("frontend/post.html")

@app.get("/style.css")
def serve_style():
    return FileResponse("frontend/style.css")

allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_conn():
    db_path = os.getenv("DATABASE_URL", "ottoke.db").replace("sqlite:///", "")
    if db_path.startswith("postgresql://"):
        db_path = "ottoke.db"
    conn = sqlite3.connect(db_path, check_same_thread=False, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

class ConfessionSubmit(BaseModel):
    content: str

class VoteSubmit(BaseModel):
    stars: int

class CommentSubmit(BaseModel):
    confession_id: int
    parent_id: Optional[int] = None
    content: str
    vibe: str

def get_ip_hash(request: Request) -> str:
    ip = request.headers.get("x-forwarded-for", request.client.host).split(",")[0]
    return hashlib.sha256(ip.encode()).hexdigest()

def get_session_id(request: Request) -> str:
    ip = request.headers.get("x-forwarded-for", request.client.host).split(",")[0]
    user_agent = request.headers.get("user-agent", "")
    return hashlib.sha256(f"{ip}-{user_agent}-ottoke-salt".encode()).hexdigest()

def check_rate_limit(conn, ip_hash: str, action: str, limit: int, hours: int = 1):
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT COUNT(*) FROM rate_limits 
        WHERE ip_hash = ? AND action = ? 
        AND created_at >= datetime('now', '-' || ? || ' hours')
        """, 
        (ip_hash, action, hours)
    )
    count = cursor.fetchone()[0]
    if count >= limit:
        raise HTTPException(status_code=429, detail="Too many requests")
    
    cursor.execute(
        "INSERT INTO rate_limits (ip_hash, action) VALUES (?, ?)",
        (ip_hash, action)
    )
    conn.commit()

@app.get("/api/confessions")
def list_confessions(page: int = 1):
    offset = (page - 1) * 20
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, content, avg_rating, rating_count, comment_count, created_at 
        FROM confessions 
        WHERE is_deleted = FALSE 
        ORDER BY created_at DESC 
        LIMIT 20 OFFSET ?
    """, (offset,))
    confessions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return confessions

@app.get("/api/confessions/{conf_id}")
def get_confession(conf_id: int):
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM confessions WHERE id = ? AND is_deleted = FALSE", (conf_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Confession not found")
    
    conf = dict(row)
    cursor.execute("""
        SELECT id, parent_id, content, vibe, created_at
        FROM comments
        WHERE confession_id = ?
        ORDER BY created_at ASC
    """, (conf_id,))
    comments = [dict(r) for r in cursor.fetchall()]
    
    conn.close()
    conf["comments"] = comments
    return conf

@app.post("/api/confessions")
def create_confession(payload: ConfessionSubmit, request: Request):
    text = payload.content.strip()
    if not text or len(text) > 500:
        raise HTTPException(status_code=400, detail="Invalid confession content")
    
    conn = get_db_conn()
    try:
        check_rate_limit(conn, get_ip_hash(request), "confession_submit", 5)
        
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO confessions (content) VALUES (?) RETURNING id",
            (text,)
        )
        new_id = cursor.fetchone()["id"]
        conn.commit()
        return {"id": new_id, "message": "Confession submitted. Your suffering has been recorded."}
    finally:
        conn.close()

@app.post("/api/confessions/{conf_id}/vote")
def vote_confession(conf_id: int, payload: VoteSubmit, request: Request):
    if not 1 <= payload.stars <= 5:
        raise HTTPException(status_code=400, detail="Stars must be 1-5")
    
    conn = get_db_conn()
    try:
        check_rate_limit(conn, get_ip_hash(request), "vote", 10)
        session_id = get_session_id(request)
        
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM confessions WHERE id = ? AND is_deleted = FALSE", (conf_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Confession not found")
        
        try:
            cursor.execute(
                "INSERT INTO votes (confession_id, stars, session_id) VALUES (?, ?, ?)",
                (conf_id, payload.stars, session_id)
            )
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Already voted")
        
        cursor.execute("""
            UPDATE confessions 
            SET rating_sum = rating_sum + ?, rating_count = rating_count + 1 
            WHERE id = ? 
            RETURNING avg_rating
        """, (payload.stars, conf_id))
        new_avg = cursor.fetchone()["avg_rating"]
        conn.commit()
        return {"new_avg_rating": round(new_avg, 1), "message": "Vote recorded."}
    finally:
        conn.close()

@app.post("/api/comments")
def add_comment(payload: CommentSubmit, request: Request):
    text = payload.content.strip()
    if not text or len(text) > 300:
        raise HTTPException(status_code=400, detail="Invalid comment content")
    if payload.vibe not in ["japan", "korea"]:
        raise HTTPException(status_code=400, detail="Invalid vibe")
    
    conn = get_db_conn()
    try:
        check_rate_limit(conn, get_ip_hash(request), "comment", 10) # 10 comments per hour
        session_id = get_session_id(request)
        
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM confessions WHERE id = ? AND is_deleted=FALSE", (payload.confession_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Confession not found")
            
        cursor.execute(
            """
            INSERT INTO comments (confession_id, parent_id, content, vibe, session_id)
            VALUES (?, ?, ?, ?, ?) RETURNING id
            """,
            (payload.confession_id, payload.parent_id, text, payload.vibe, session_id)
        )
        new_id = cursor.fetchone()["id"]
        
        cursor.execute("UPDATE confessions SET comment_count = comment_count + 1 WHERE id = ?", (payload.confession_id,))
        conn.commit()
        return {"id": new_id, "vibe": payload.vibe, "message": "Comment added"}
    finally:
        conn.close()

@app.get("/api/leaderboard")
def get_leaderboard(timeframe: str = Query("all")):
    conn = get_db_conn()
    cursor = conn.cursor()
    query = """
        SELECT id, content, avg_rating, comment_count, rating_count
        FROM confessions
        WHERE is_deleted = FALSE AND rating_count > 0
    """
    if timeframe == "week":
        query += " AND created_at >= datetime('now', '-7 days') "
        
    query += " ORDER BY avg_rating DESC, rating_count DESC LIMIT 10"
    cursor.execute(query)
    data = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return data

@app.get("/api/daily-quote")
def get_daily_quote():
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, quote, source, type FROM daily_quotes WHERE used_at = CURRENT_DATE LIMIT 1")
    row = cursor.fetchone()
    
    if not row:
        cursor.execute("UPDATE daily_quotes SET used_at = NULL WHERE used_at = datetime('now', '-1 day')")
        cursor.execute("SELECT id, quote, source, type FROM daily_quotes WHERE used_at IS NULL ORDER BY RANDOM() LIMIT 1")
        row = cursor.fetchone()
        
        if not row:
            cursor.execute("UPDATE daily_quotes SET used_at = NULL")
            cursor.execute("SELECT id, quote, source, type FROM daily_quotes WHERE used_at IS NULL ORDER BY RANDOM() LIMIT 1")
            row = cursor.fetchone()
            
        if row:
            cursor.execute("UPDATE daily_quotes SET used_at = CURRENT_DATE WHERE id = ?", (row["id"],))
            conn.commit()
            
    conn.close()
    return dict(row) if row else {"quote": "Fighting!", "source": "Every K-drama ever", "type": "kdrama"}

@app.get("/api/stats")
def get_stats():
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) as cx FROM confessions")
    cx = cursor.fetchone()["cx"]
    cursor.execute("SELECT count(*) as vx FROM votes")
    vx = cursor.fetchone()["vx"]
    cursor.execute("SELECT count(*) as cmx FROM comments")
    cmx = cursor.fetchone()["cmx"]
    conn.close()
    return {"total_confessions": cx, "total_votes": vx, "total_comments": cmx}

@app.get("/api/cron/daily-quote")
def rotate_daily_quote():
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM daily_quotes WHERE used_at IS NULL ORDER BY RANDOM() LIMIT 1")
    row = cursor.fetchone()
    if not row:
        cursor.execute("UPDATE daily_quotes SET used_at = NULL")
        cursor.execute("SELECT id FROM daily_quotes WHERE used_at IS NULL ORDER BY RANDOM() LIMIT 1")
        row = cursor.fetchone()
        
    if row:
        cursor.execute("UPDATE daily_quotes SET used_at = NULL WHERE used_at = CURRENT_DATE")
        cursor.execute("UPDATE daily_quotes SET used_at = CURRENT_DATE WHERE id = ?", (row["id"],))
    conn.commit()
    conn.close()
    return {"status": "ok"}
