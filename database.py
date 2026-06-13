import sqlite3
from datetime import datetime

DB_PATH = "joged_afiliasi.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS videos (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            judul       TEXT NOT NULL,
            deskripsi   TEXT,
            link_video  TEXT NOT NULL,
            link_shopee TEXT NOT NULL,
            dibuat_pada TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS klik_log (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id   INTEGER NOT NULL,
            user_id    INTEGER NOT NULL,
            waktu      TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (video_id) REFERENCES videos(id)
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database siap.")

def get_all_videos():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM videos ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_video_by_id(video_id: int):
    conn = get_conn()
    row = conn.execute("SELECT * FROM videos WHERE id = ?", (video_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def add_video(judul: str, deskripsi: str, link_video: str, link_shopee: str):
    conn = get_conn()
    conn.execute(
        "INSERT INTO videos (judul, deskripsi, link_video, link_shopee) VALUES (?, ?, ?, ?)",
        (judul, deskripsi, link_video, link_shopee)
    )
    conn.commit()
    conn.close()

def delete_video(video_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM videos WHERE id = ?", (video_id,))
    conn.execute("DELETE FROM klik_log WHERE video_id = ?", (video_id,))
    conn.commit()
    conn.close()

def log_click(video_id: int, user_id: int):
    conn = get_conn()
    conn.execute(
        "INSERT INTO klik_log (video_id, user_id) VALUES (?, ?)",
        (video_id, user_id)
    )
    conn.commit()
    conn.close()

def get_stats():
    conn = get_conn()
    rows = conn.execute("""
        SELECT v.judul, COUNT(k.id) as total_klik
        FROM videos v
        LEFT JOIN klik_log k ON v.id = k.video_id
        GROUP BY v.id
        ORDER BY total_klik DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]
