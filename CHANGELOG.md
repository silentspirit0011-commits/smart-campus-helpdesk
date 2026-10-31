# Changelog — Smart Campus HelpDesk

All notable changes to the backend, database architecture, and frontend integrations are documented here in beginner-friendly terms.

---

## [Phase 2 Implementation] - 2026-10-14

### Added
- **Database Layer (`database.py`):**
  - Designed an embedded SQLite database (`campus_complaints.db`) using Python's standard library.
  - Implemented 3 structured tables:
    1. `complaints`: Stores tracking ID, student details, title, category, priority, location, description, status, and timestamps.
    2. `complaint_history`: An audit table logging every status change (old status, new status, timestamp, responsible admin, and remarks).
    3. `admins`: Stores administrator usernames and password hashes.
  - Added parameterized SQL queries everywhere to guarantee 100% protection against SQL Injection attacks.
  - Added password hashing using `werkzeug.security` (`generate_password_hash` and `check_password_hash`) so plain-text passwords are never stored.

- **Backend APIs (`app.py`):**
  - `POST /api/complaints`: Handles student submissions with full server-side validation (name, email format, category, priority, text lengths) and generates unique tracking IDs (`CMP-XXXXXX`).
  - `GET /api/complaints/<tracking_id>`: Looks up a complaint by its tracking ID and returns its status and public details safely.
  - `GET /api/complaints`: Protected admin endpoint that loads all complaints from the database for the admin dashboard.
  - `POST /api/complaints/<tracking_id>/status`: Protected admin endpoint that changes a complaint's status (`Pending`, `In Progress`, `Resolved`) and logs the change to the audit history table.
  - `GET /api/complaints/statistics`: Protected admin endpoint calculating real-time counts (`total`, `pending`, `in_progress`, `resolved`).
  - `POST /admin/login` & `GET /admin/logout`: Secure session-based authentication system preventing unauthorized access to the admin dashboard.

- **Frontend Integration (`static/js/`):**
  - Connected `templates/complaint.html` to `complaint-api.js` to allow students to submit real complaints and receive clickable tracking IDs.
  - Connected `templates/track.html` to `track-api.js` to query live database records and auto-fill tracking IDs from URL query parameters (`/track?id=CMP-...`).
  - Implemented `admin-api.js` for `templates/admin.html`, replacing dummy static arrays with live data fetching, real-time status updating, and live metric cards.
  - Created `templates/login.html` matching Member 1's visual theme for administrator authentication.

- **Security & Configuration:**
  - Added `.gitignore` to prevent leaking secrets (`.env`, `credentials.txt`), local databases (`*.db`), or cache directories to version control.
  - Added `.env.example` and `.env` for configurable secrets and credentials.
  - Added `requirements.txt` listing minimal dependencies (`Flask`, `python-dotenv`, `pytest`, `Werkzeug`).
