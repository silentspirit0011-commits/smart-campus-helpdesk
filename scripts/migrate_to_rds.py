import os
import sqlite3
from dotenv import load_dotenv
load_dotenv(".env")
import database

def migrate():
    db_file = "campus_complaints.db"
    if not os.path.exists(db_file):
        print(f"No SQLite file found at {db_file}.")
        return

    sconn = sqlite3.connect(db_file)
    sconn.row_factory = sqlite3.Row
    scur = sconn.cursor()

    try:
        rows = scur.execute("SELECT * FROM complaints").fetchall()
    except Exception as e:
        print("Could not read SQLite complaints table:", e)
        sconn.close()
        return

    print(f"Found {len(rows)} complaints in local SQLite database.")
    if not rows:
        sconn.close()
        return

    if not database.is_rds():
        print("Error: RDS is not connected! DB_HOST not found in environment.")
        sconn.close()
        return

    rconn = database.get_db()
    rcur = rconn.cursor()

    imported = 0
    for r in rows:
        tracking_id = r["tracking_id"]
        rcur.execute("SELECT id FROM complaints WHERE tracking_id = %s", (tracking_id,))
        if rcur.fetchone():
            print(f"Skipping {tracking_id} (already in RDS)")
            continue

        rcur.execute("""
            INSERT INTO complaints (
                tracking_id, student_name, student_email, title,
                category, priority, location, description, image_filename,
                status, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            tracking_id,
            r["student_name"],
            r["student_email"],
            r["title"],
            r["category"],
            r["priority"],
            r["location"],
            r["description"],
            r["image_filename"] if "image_filename" in r.keys() else None,
            r["status"],
            r["created_at"],
            r["created_at"]
        ))
        imported += 1

    print(f"Successfully migrated {imported} complaints into Amazon RDS MySQL!")
    rconn.close()
    sconn.close()

if __name__ == "__main__":
    migrate()
