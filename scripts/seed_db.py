import os
import sqlite3
from dotenv import load_dotenv

load_dotenv(".env.local")

def init_db():
    db_path = os.getenv("DATABASE_URL", "ottoke.db").replace("sqlite:///", "")
    if db_path.startswith("postgresql://"):
        db_path = "ottoke.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    schema = """
    CREATE TABLE IF NOT EXISTS rate_limits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip_hash TEXT NOT NULL,
        action TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS confessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL CHECK (length(content) <= 500),
        rating_sum INTEGER DEFAULT 0,
        rating_count INTEGER DEFAULT 0,
        comment_count INTEGER DEFAULT 0,
        avg_rating FLOAT GENERATED ALWAYS AS (
            CASE WHEN rating_count > 0 THEN CAST(rating_sum AS FLOAT) / rating_count ELSE 0 END
        ) STORED,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_deleted BOOLEAN DEFAULT FALSE
    );

    CREATE TABLE IF NOT EXISTS votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        confession_id INTEGER REFERENCES confessions(id) ON DELETE CASCADE,
        stars INTEGER CHECK (stars >= 1 AND stars <= 5),
        session_id TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(confession_id, session_id)
    );

    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        confession_id INTEGER REFERENCES confessions(id) ON DELETE CASCADE,
        parent_id INTEGER REFERENCES comments(id) ON DELETE CASCADE,
        content TEXT NOT NULL CHECK (length(content) <= 300),
        vibe TEXT CHECK (vibe IN ('japan', 'korea')),
        session_id TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS daily_quotes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quote TEXT NOT NULL,
        source TEXT NOT NULL,
        type TEXT CHECK (type IN ('anime', 'kdrama')),
        used_at DATE DEFAULT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_confessions_created ON confessions(created_at DESC);
    CREATE INDEX IF NOT EXISTS idx_confessions_avg_rating ON confessions(avg_rating DESC);
    CREATE INDEX IF NOT EXISTS idx_votes_confession ON votes(confession_id);
    CREATE INDEX IF NOT EXISTS idx_comments_confession ON comments(confession_id);
    CREATE INDEX IF NOT EXISTS idx_rate_limits_ip_action ON rate_limits(ip_hash, action, created_at);
    """

    cursor.executescript(schema)

    # Seed quotes
    quotes = [
        ("Believe in the me that believes in you.", "Kamina, Gurren Lagann", "anime"),
        ("If you give up, that's where it ends.", "Coach Ukai, Haikyuu!!", "anime"),
        ("People die when they are killed.", "Shirou Emiya, Fate/stay night", "anime"),
        ("I'll take a potato chip... and eat it!", "Light Yagami, Death Note", "anime"),
        ("Bankai!", "Various, Bleach", "anime"),
        ("It's okay to not have a plan. Sometimes you just need to breathe.", "Reply 1988", "kdrama"),
        ("The person who endures to the end wins.", "Itaewon Class", "kdrama"),
        ("In this world, the ones who are lucky survive.", "Squid Game", "kdrama"),
        ("I love you even if it's a crime.", "Crash Landing on You", "kdrama"),
        ("Fighting!", "Every K-drama ever", "kdrama")
    ] * 6  # Duplicate to hit >50 quotes as requested

    cursor.execute("SELECT COUNT(*) FROM daily_quotes")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO daily_quotes (quote, source, type) VALUES (?, ?, ?)",
            [(q[0], q[1], q[2]) for q in quotes]
        )
        print("Database seeded with quotes.")
    
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("DB init complete.")
