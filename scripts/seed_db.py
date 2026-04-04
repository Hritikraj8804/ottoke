import os
import sys
from dotenv import load_dotenv

load_dotenv(".env.local")

def init_db():
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # Check if we're using PostgreSQL (RDS) or SQLite (local)
    if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
        print("📦 Using PostgreSQL (RDS)...")
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        
        # PostgreSQL schema
        schema = """
        CREATE TABLE IF NOT EXISTS rate_limits (
            id SERIAL PRIMARY KEY,
            ip_hash TEXT NOT NULL,
            action TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS confessions (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            rating_sum INTEGER DEFAULT 0,
            rating_count INTEGER DEFAULT 0,
            comment_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_deleted BOOLEAN DEFAULT FALSE
        );

        CREATE TABLE IF NOT EXISTS votes (
            id SERIAL PRIMARY KEY,
            confession_id INTEGER REFERENCES confessions(id) ON DELETE CASCADE,
            stars INTEGER NOT NULL,
            session_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(confession_id, session_id)
        );

        CREATE TABLE IF NOT EXISTS comments (
            id SERIAL PRIMARY KEY,
            confession_id INTEGER REFERENCES confessions(id) ON DELETE CASCADE,
            parent_id INTEGER REFERENCES comments(id) ON DELETE CASCADE,
            content TEXT NOT NULL,
            vibe TEXT CHECK (vibe IN ('japan', 'korea')),
            session_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS daily_quotes (
            id SERIAL PRIMARY KEY,
            quote TEXT NOT NULL,
            source TEXT NOT NULL,
            type TEXT CHECK (type IN ('anime', 'kdrama')),
            used_at DATE DEFAULT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_confessions_created ON confessions(created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_comments_confession ON comments(confession_id);
        CREATE INDEX IF NOT EXISTS idx_rate_limits_ip_action ON rate_limits(ip_hash, action, created_at);
        """
        
        cursor.execute(schema)
        
        # Seed quotes for PostgreSQL
        quotes = [
            ("Believe in the me that believes in you.", "Kamina, Gurren Lagann", "anime"),
            ("If you give up, that's where it ends.", "Coach Ukai, Haikyuu!!", "anime"),
            ("People die when they are killed.", "Shirou Emiya, Fate/stay night", "anime"),
            ("I'll take a potato chip... and eat it!", "Light Yagami, Death Note", "anime"),
            ("Bankai!", "Various, Bleach", "anime"),
            ("It's over 9000!", "Vegeta, Dragon Ball Z", "anime"),
            ("I am the bone of my sword.", "Archer, Fate/stay night", "anime"),
            ("Yare yare daze.", "Jotaro Kujo, JoJo's Bizarre Adventure", "anime"),
            ("Omae wa mou shindeiru.", "Kenshiro, Fist of the North Star", "anime"),
            ("NANI?!", "Various, Anime", "anime"),
            ("It's okay to not have a plan. Sometimes you just need to breathe.", "Reply 1988", "kdrama"),
            ("The person who endures to the end wins.", "Itaewon Class", "kdrama"),
            ("In this world, the ones who are lucky survive.", "Squid Game", "kdrama"),
            ("Fighting!", "Every K-drama ever", "kdrama"),
            ("Ottoke?! (What to do?!)", "Korean phrase", "kdrama"),
            ("Aish...", "Korean expression of frustration", "kdrama"),
            ("Daebak!", "Korean expression for awesome", "kdrama"),
            ("You must be out of your mind!", "Crash Landing on You", "kdrama"),
            ("I love you even if it's a crime.", "Crash Landing on You", "kdrama"),
            ("The world is full of survivors.", "Squid Game", "kdrama"),
            ("You came into my life like a gift.", "Goblin", "kdrama"),
            ("Every moment I spent with you was a miracle.", "Crash Landing on You", "kdrama"),
        ]
        
        cursor.execute("SELECT COUNT(*) FROM daily_quotes")
        count = cursor.fetchone()["count"]
        
        if count == 0:
            for quote, source, qtype in quotes:
                cursor.execute(
                    "INSERT INTO daily_quotes (quote, source, type) VALUES (%s, %s, %s)",
                    (quote, source, qtype)
                )
            print(f"✅ Seeded {len(quotes)} quotes to PostgreSQL")
        else:
            print(f"✅ Database already has {count} quotes")
        
        conn.commit()
        cursor.close()
        conn.close()
        print("🎉 PostgreSQL (RDS) database ready!")
        
    else:
        print("📦 Using SQLite (local)...")
        import sqlite3
        
        db_path = os.getenv("DATABASE_URL", "ottoke.db").replace("sqlite:///", "")
        if db_path.startswith("postgresql://"):
            db_path = "ottoke.db"
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # SQLite schema
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
        
        # Seed quotes for SQLite
        quotes = [
            ("Believe in the me that believes in you.", "Kamina, Gurren Lagann", "anime"),
            ("If you give up, that's where it ends.", "Coach Ukai, Haikyuu!!", "anime"),
            ("People die when they are killed.", "Shirou Emiya, Fate/stay night", "anime"),
            ("I'll take a potato chip... and eat it!", "Light Yagami, Death Note", "anime"),
            ("Bankai!", "Various, Bleach", "anime"),
            ("It's over 9000!", "Vegeta, Dragon Ball Z", "anime"),
            ("I am the bone of my sword.", "Archer, Fate/stay night", "anime"),
            ("Yare yare daze.", "Jotaro Kujo, JoJo's Bizarre Adventure", "anime"),
            ("Omae wa mou shindeiru.", "Kenshiro, Fist of the North Star", "anime"),
            ("NANI?!", "Various, Anime", "anime"),
            ("It's okay to not have a plan. Sometimes you just need to breathe.", "Reply 1988", "kdrama"),
            ("The person who endures to the end wins.", "Itaewon Class", "kdrama"),
            ("In this world, the ones who are lucky survive.", "Squid Game", "kdrama"),
            ("Fighting!", "Every K-drama ever", "kdrama"),
            ("Ottoke?! (What to do?!)", "Korean phrase", "kdrama"),
            ("Aish...", "Korean expression of frustration", "kdrama"),
            ("Daebak!", "Korean expression for awesome", "kdrama"),
            ("You must be out of your mind!", "Crash Landing on You", "kdrama"),
            ("I love you even if it's a crime.", "Crash Landing on You", "kdrama"),
            ("The world is full of survivors.", "Squid Game", "kdrama"),
            ("You came into my life like a gift.", "Goblin", "kdrama"),
            ("Every moment I spent with you was a miracle.", "Crash Landing on You", "kdrama"),
        ]
        
        cursor.execute("SELECT COUNT(*) FROM daily_quotes")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO daily_quotes (quote, source, type) VALUES (?, ?, ?)",
                quotes
            )
            print(f"✅ Seeded {len(quotes)} quotes to SQLite")
        else:
            print("✅ Database already has quotes")
        
        conn.commit()
        cursor.close()
        conn.close()
        print("🎉 SQLite database ready!")

if __name__ == "__main__":
    init_db()
    print("DB init complete.")