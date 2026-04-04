import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check which database to use
DATABASE_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    """Returns database connection (SQLite or PostgreSQL)"""
    
    if DATABASE_URL:
        # Use PostgreSQL (RDS in production)
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    else:
        # Use SQLite (local development)
        conn = sqlite3.connect('ottoke.db')
        conn.row_factory = sqlite3.Row
        return conn