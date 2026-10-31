import os, sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

DB_HOST = os.environ.get("DB_HOST") or os.environ.get("RDS_HOST")
DB_USER = os.environ.get("DB_USER", "admin")
DB_PASS = os.environ.get("DB_PASSWORD", "")
DB_NAME = os.environ.get("DB_NAME", "campus_complaints")
DB_PORT = int(os.environ.get("DB_PORT", 3306))
SQLITE_PATH = os.environ.get("DATABASE_PATH", "campus_complaints.db")

def is_rds():
    return bool(os.environ.get("DB_HOST") or os.environ.get("RDS_HOST"))

def get_db(db_path=None):
    if is_rds():
        import pymysql, pymysql.cursors
        host = os.environ.get("DB_HOST") or os.environ.get("RDS_HOST")
        user = os.environ.get("DB_USER", "admin")
        pwd = os.environ.get("DB_PASSWORD", "")
        name = os.environ.get("DB_NAME", "campus_complaints")
        port = int(os.environ.get("DB_PORT", 3306))
        try:
            return pymysql.connect(host=host, user=user, password=pwd, database=name, port=port, cursorclass=pymysql.cursors.DictCursor, autocommit=True)
        except pymysql.err.OperationalError as e:
            if e.args[0] == 1049:
                rconn = pymysql.connect(host=host, user=user, password=pwd, port=port, autocommit=True)
                with rconn.cursor() as c:
                    c.execute("CREATE DATABASE IF NOT EXISTS campus_complaints DEFAULT CHARACTER SET utf8mb4;")
                rconn.close()
                return pymysql.connect(host=host, user=user, password=pwd, database=name, port=port, cursorclass=pymysql.cursors.DictCursor, autocommit=True)
            raise e
    path = db_path or os.environ.get("DATABASE_PATH", SQLITE_PATH)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db(db_path=None):
    conn = get_db(db_path)
    cur = conn.cursor()
    if is_rds():
        cur.execute("""CREATE TABLE IF NOT EXISTS complaints (
            id INT AUTO_INCREMENT PRIMARY KEY, tracking_id VARCHAR(50) UNIQUE NOT NULL,
            student_name VARCHAR(100) NOT NULL, student_email VARCHAR(255) NOT NULL,
            title VARCHAR(150) NOT NULL, category VARCHAR(50) NOT NULL,
            priority VARCHAR(20) NOT NULL, location VARCHAR(200) NOT NULL,
            description TEXT NOT NULL, image_filename VARCHAR(255),
            status VARCHAR(30) NOT NULL DEFAULT 'Pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP, updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;""")
        cur.execute("""CREATE TABLE IF NOT EXISTS complaint_history (
            id INT AUTO_INCREMENT PRIMARY KEY, complaint_id INT NOT NULL, tracking_id VARCHAR(50) NOT NULL,
            old_status VARCHAR(30) NOT NULL, new_status VARCHAR(30) NOT NULL, remarks TEXT,
            changed_by VARCHAR(100) NOT NULL, changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (complaint_id) REFERENCES complaints (id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;""")
        cur.execute("""CREATE TABLE IF NOT EXISTS admins (
            id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;""")
    else:
        cur.execute("""CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT, tracking_id TEXT UNIQUE NOT NULL,
            student_name TEXT NOT NULL, student_email TEXT NOT NULL, title TEXT NOT NULL,
            category TEXT NOT NULL, priority TEXT NOT NULL, location TEXT NOT NULL,
            description TEXT NOT NULL, image_filename TEXT, status TEXT NOT NULL DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""")
        cur.execute("""CREATE TABLE IF NOT EXISTS complaint_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT, complaint_id INTEGER NOT NULL, tracking_id TEXT NOT NULL,
            old_status TEXT NOT NULL, new_status TEXT NOT NULL, remarks TEXT, changed_by TEXT NOT NULL,
            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (complaint_id) REFERENCES complaints (id) ON DELETE CASCADE
        );""")
        cur.execute("""CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""")
        conn.commit()
    conn.close()

def seed_default_admin(username=None, password=None, db_path=None):
    u = username or os.environ.get("ADMIN_USERNAME", "admin")
    p = password or os.environ.get("ADMIN_PASSWORD", "adminpassword123")
    conn = get_db(db_path)
    cur = conn.cursor()
    ph = "%s" if is_rds() else "?"
    cur.execute(f"SELECT id FROM admins WHERE username = {ph}", (u,))
    row = cur.fetchone()
    h = generate_password_hash(p)
    if row:
        cur.execute(f"UPDATE admins SET password_hash = {ph} WHERE username = {ph}", (h, u))
    else:
        cur.execute(f"INSERT INTO admins (username, password_hash) VALUES ({ph}, {ph})", (u, h))
    if not is_rds(): conn.commit()
    conn.close()

def verify_admin_credentials(username, password, db_path=None):
    conn = get_db(db_path)
    cur = conn.cursor()
    ph = "%s" if is_rds() else "?"
    cur.execute(f"SELECT password_hash FROM admins WHERE username = {ph}", (username,))
    row = cur.fetchone()
    conn.close()
    return bool(row and check_password_hash(row["password_hash"], password))

def generate_tracking_id(db_path=None):
    conn = get_db(db_path)
    cur = conn.cursor()
    ph = "%s" if is_rds() else "?"
    while True:
        cur.execute("SELECT MAX(id) AS m FROM complaints")
        r = cur.fetchone()
        val = (r["m"] if is_rds() else r[0]) or 0
        cid = f"CMP-{val + 101:06d}"
        cur.execute(f"SELECT 1 FROM complaints WHERE tracking_id = {ph}", (cid,))
        if not cur.fetchone():
            conn.close()
            return cid

def create_complaint(data, db_path=None):
    cid = generate_tracking_id(db_path)
    conn = get_db(db_path)
    cur = conn.cursor()
    ph = "%s" if is_rds() else "?"
    cur.execute(f"""INSERT INTO complaints (
        tracking_id, student_name, student_email, title, category, priority, location, description, image_filename, status
    ) VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, 'Pending')""", (
        cid, data.get("student_name", "").strip(), data.get("student_email", "").strip(),
        data.get("title", "").strip(), data.get("category", "").strip(), data.get("priority", "").strip(),
        data.get("location", "").strip(), data.get("description", "").strip(), data.get("image_filename")
    ))
    lid = cur.lastrowid
    cur.execute(f"""INSERT INTO complaint_history (
        complaint_id, tracking_id, old_status, new_status, remarks, changed_by
    ) VALUES ({ph}, {ph}, 'None', 'Pending', 'Complaint submitted', 'System')""", (lid, cid))
    if not is_rds(): conn.commit()
    conn.close()
    return cid

def get_complaint_by_tracking_id(tracking_id, db_path=None):
    conn = get_db(db_path)
    cur = conn.cursor()
    ph = "%s" if is_rds() else "?"
    cur.execute(f"SELECT tracking_id, title, category, priority, location, status, created_at, updated_at FROM complaints WHERE tracking_id = {ph}", (tracking_id.strip(),))
    r = cur.fetchone()
    conn.close()
    if not r: return None
    d = dict(r)
    for k in ("created_at", "updated_at"):
        if isinstance(d.get(k), datetime): d[k] = d[k].strftime("%Y-%m-%d %H:%M:%S")
    return d

def get_all_complaints(db_path=None):
    conn = get_db(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, tracking_id, title, category, priority, location, status, student_name, student_email, description, created_at FROM complaints ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    out = []
    for r in rows:
        d = dict(r)
        d["id"] = d["tracking_id"]
        if isinstance(d.get("created_at"), datetime): d["created_at"] = d["created_at"].strftime("%Y-%m-%d %H:%M:%S")
        else: d["created_at"] = str(d.get("created_at", ""))
        out.append(d)
    return out

def get_complaint_statistics(db_path=None):
    conn = get_db(db_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS total FROM complaints")
    t = (cur.fetchone()["total"] if is_rds() else cur.fetchone()[0])
    cur.execute("SELECT COUNT(*) AS pending FROM complaints WHERE status = 'Pending'")
    p = (cur.fetchone()["pending"] if is_rds() else cur.fetchone()[0])
    cur.execute("SELECT COUNT(*) AS in_prog FROM complaints WHERE status = 'In Progress'")
    ip = (cur.fetchone()["in_prog"] if is_rds() else cur.fetchone()[0])
    cur.execute("SELECT COUNT(*) AS resolved FROM complaints WHERE status = 'Resolved'")
    res = (cur.fetchone()["resolved"] if is_rds() else cur.fetchone()[0])
    conn.close()
    return {"total": t, "pending": p, "in_progress": ip, "resolved": res}

def update_complaint_status(tracking_id, new_status, remarks=None, changed_by="Admin", db_path=None):
    if new_status not in ["Pending", "In Progress", "Resolved"]: raise ValueError("Invalid status")
    conn = get_db(db_path)
    cur = conn.cursor()
    ph = "%s" if is_rds() else "?"
    cur.execute(f"SELECT id, status FROM complaints WHERE tracking_id = {ph}", (tracking_id.strip(),))
    r = cur.fetchone()
    if not r: conn.close(); return False
    old_s, lid = r["status"], r["id"]
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute(f"UPDATE complaints SET status = {ph}, updated_at = {ph} WHERE id = {ph}", (new_status, now, lid))
    cur.execute(f"INSERT INTO complaint_history (complaint_id, tracking_id, old_status, new_status, remarks, changed_by, changed_at) VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})", (lid, tracking_id, old_s, new_status, remarks or f"Status changed to {new_status}", changed_by, now))
    if not is_rds(): conn.commit()
    conn.close()
    return True

def get_complaint_history(tracking_id, db_path=None):
    conn = get_db(db_path)
    cur = conn.cursor()
    ph = "%s" if is_rds() else "?"
    cur.execute(f"SELECT old_status, new_status, remarks, changed_by, changed_at FROM complaint_history WHERE tracking_id = {ph} ORDER BY id ASC", (tracking_id.strip(),))
    rows = cur.fetchall()
    conn.close()
    out = []
    for r in rows:
        d = dict(r)
        if isinstance(d.get("changed_at"), datetime): d["changed_at"] = d["changed_at"].strftime("%Y-%m-%d %H:%M:%S")
        out.append(d)
    return out
