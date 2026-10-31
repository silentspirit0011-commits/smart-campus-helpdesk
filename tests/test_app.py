import os
import tempfile
import pytest
from app import app
import database


@pytest.fixture
def client():
    """Configure a fresh test client and temporary SQLite database for each test."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["DATABASE_PATH"] = db_path
    os.environ["DATABASE_PATH"] = db_path

    # Initialize schema and admin account in test DB
    database.init_db(db_path=db_path)
    database.seed_default_admin(username="admin", password="adminpassword123", db_path=db_path)

    with app.test_client() as test_client:
        yield test_client

    if os.path.exists(db_path):
        os.remove(db_path)


# ==============================================================================
# 1. Valid Submission & Missing/Invalid Fields Validation
# ==============================================================================

def test_valid_submission(client):
    """Test valid complaint submission creates record and returns unique tracking ID."""
    payload = {
        "student_name": "Rohan Sharma",
        "student_email": "rohan@campus.edu",
        "title": "Lab 3 Projector Display Flickering",
        "category": "Classroom Equipment",
        "priority": "High",
        "location": "Academic Block A, Room 302",
        "description": "The HDMI input cuts out every 2 minutes during lectures."
    }

    response = client.post("/api/complaints", data=payload)
    assert response.status_code == 201

    json_data = response.get_json()
    assert json_data["success"] is True
    assert "complaint_id" in json_data
    assert json_data["complaint_id"].startswith("CMP-")


def test_missing_and_invalid_fields(client):
    """Test server rejects missing required fields and invalid email formats."""
    # Missing student name
    resp = client.post("/api/complaints", data={
        "student_email": "test@campus.edu",
        "title": "Broken bench",
        "category": "Infrastructure",
        "priority": "Low",
        "location": "Library",
        "description": "Wood is cracked"
    })
    assert resp.status_code == 400
    assert resp.get_json()["success"] is False

    # Invalid email address
    resp = client.post("/api/complaints", data={
        "student_name": "Alice",
        "student_email": "not-a-valid-email",
        "title": "Broken bench",
        "category": "Other",
        "priority": "Low",
        "location": "Library",
        "description": "Wood is cracked"
    })
    assert resp.status_code == 400
    assert "email" in resp.get_json()["message"].lower()

    # Invalid category
    resp = client.post("/api/complaints", data={
        "student_name": "Alice",
        "student_email": "alice@campus.edu",
        "title": "Broken bench",
        "category": "FakeCategory123",
        "priority": "Low",
        "location": "Library",
        "description": "Wood is cracked"
    })
    assert resp.status_code == 400
    assert "category" in resp.get_json()["message"].lower()


# ==============================================================================
# 2. Unique Tracking IDs
# ==============================================================================

def test_unique_tracking_ids(client):
    """Ensure consecutive complaint submissions produce strictly distinct tracking IDs."""
    ids = set()
    for i in range(5):
        payload = {
            "student_name": f"Student {i}",
            "student_email": f"student{i}@campus.edu",
            "title": f"Complaint Title {i}",
            "category": "Electrical",
            "priority": "Medium",
            "location": f"Hostel Room {100 + i}",
            "description": f"Details for issue number {i}"
        }
        res = client.post("/api/complaints", data=payload)
        assert res.status_code == 201
        cid = res.get_json()["complaint_id"]
        assert cid not in ids
        ids.add(cid)
    assert len(ids) == 5


# ==============================================================================
# 3. Tracking Valid ID vs Invalid ID
# ==============================================================================

def test_tracking_valid_and_invalid_id(client):
    """Test public status lookup for existing and nonexistent tracking IDs."""
    # Submit a complaint first
    payload = {
        "student_name": "Priya Patel",
        "student_email": "priya@campus.edu",
        "title": "Wi-Fi Router Down in Reading Hall",
        "category": "Wi-Fi / Internet",
        "priority": "High",
        "location": "Library Ground Floor",
        "description": "No SSID broadcast visible."
    }
    submit_res = client.post("/api/complaints", data=payload)
    cid = submit_res.get_json()["complaint_id"]

    # Valid tracking lookup
    track_res = client.get(f"/api/complaints/{cid}")
    assert track_res.status_code == 200
    track_data = track_res.get_json()
    assert track_data["success"] is True
    assert track_data["complaint"]["tracking_id"] == cid
    assert track_data["complaint"]["status"] == "Pending"
    assert track_data["complaint"]["title"] == payload["title"]

    # Invalid tracking lookup
    bad_res = client.get("/api/complaints/CMP-99999999")
    assert bad_res.status_code == 404
    bad_data = bad_res.get_json()
    assert bad_data["success"] is False


# ==============================================================================
# 4. Data Persistence After App / Connection Restart
# ==============================================================================

def test_data_persistence_after_restart(client):
    """Verify that committed complaint records persist across database reconnects."""
    db_path = app.config["DATABASE_PATH"]

    payload = {
        "student_name": "Siddharth Rao",
        "student_email": "sid@campus.edu",
        "title": "Hostel Water Purifier Filter Service Needed",
        "category": "Plumbing",
        "priority": "Medium",
        "location": "Boys Hostel 2, Floor 1",
        "description": "Flow rate has dropped to a trickle."
    }
    res = client.post("/api/complaints", data=payload)
    cid = res.get_json()["complaint_id"]

    # Directly re-open SQLite database as if the app was restarted
    reopened_complaint = database.get_complaint_by_tracking_id(cid, db_path=db_path)
    assert reopened_complaint is not None
    assert reopened_complaint["tracking_id"] == cid
    assert reopened_complaint["title"] == payload["title"]
    assert reopened_complaint["status"] == "Pending"


# ==============================================================================
# 5. Admin Login Success & Failure
# ==============================================================================

def test_admin_login_success_and_failure(client):
    """Test admin authentication with valid and invalid credentials."""
    # Failure with wrong password
    bad_login = client.post("/admin/login", data={
        "username": "admin",
        "password": "wrongpassword"
    }, follow_redirects=True)
    assert b"Invalid administrator username or password" in bad_login.data

    # Success with correct credentials
    good_login = client.post("/admin/login", data={
        "username": "admin",
        "password": "adminpassword123"
    }, follow_redirects=False)
    assert good_login.status_code == 302
    assert "/admin" in good_login.headers["Location"]


# ==============================================================================
# 6. Unauthorized Admin Operations Rejected
# ==============================================================================

def test_unauthorized_admin_operations_rejected(client):
    """Ensure protected admin endpoints reject unauthenticated access."""
    # API endpoints require auth
    api_res = client.get("/api/complaints")
    assert api_res.status_code == 401

    stat_res = client.get("/api/complaints/statistics")
    assert stat_res.status_code == 401

    status_update_res = client.post("/api/complaints/CMP-000101/status", json={"status": "Resolved"})
    assert status_update_res.status_code == 401

    # Admin dashboard redirects unauthenticated browser requests to login
    dash_res = client.get("/admin", follow_redirects=False)
    assert dash_res.status_code == 302
    assert "/admin/login" in dash_res.headers["Location"]


# ==============================================================================
# 7. Successful Status Update & Audit Trail
# ==============================================================================

def test_successful_status_update_and_audit(client):
    """Test authorized admin can transition status and record audit history."""
    db_path = app.config["DATABASE_PATH"]

    # 1. Create complaint
    submit = client.post("/api/complaints", data={
        "student_name": "Deepak Verma",
        "student_email": "deepak@campus.edu",
        "title": "Air Conditioner in Seminar Hall Not Cooling",
        "category": "Electrical",
        "priority": "High",
        "location": "Admin Block Floor 3",
        "description": "Temperature remains high despite running."
    })
    cid = submit.get_json()["complaint_id"]

    # 2. Login as admin
    client.post("/admin/login", data={"username": "admin", "password": "adminpassword123"})

    # 3. Update status to 'In Progress'
    update_res = client.post(f"/api/complaints/{cid}/status", json={
        "status": "In Progress",
        "remarks": "Technician assigned to inspect refrigerant."
    })
    assert update_res.status_code == 200
    assert update_res.get_json()["status"] == "In Progress"

    # Verify status changed in public tracking lookup
    track_check = client.get(f"/api/complaints/{cid}")
    assert track_check.get_json()["complaint"]["status"] == "In Progress"

    # Verify audit history logged
    history = database.get_complaint_history(cid, db_path=db_path)
    assert len(history) == 2  # initial submission + admin update
    assert history[1]["old_status"] == "Pending"
    assert history[1]["new_status"] == "In Progress"
    assert history[1]["changed_by"] == "admin"

    # 4. Update status to 'Resolved'
    resolve_res = client.post(f"/api/complaints/{cid}/status", json={
        "status": "Resolved",
        "remarks": "Refrigerant refilled and tested."
    })
    assert resolve_res.status_code == 200
    assert resolve_res.get_json()["status"] == "Resolved"

    # 5. Reject invalid status
    invalid_res = client.post(f"/api/complaints/{cid}/status", json={"status": "ClosedPermanently"})
    assert invalid_res.status_code == 400


# ==============================================================================
# 8. Dashboard Statistics Counts
# ==============================================================================

def test_dashboard_statistics(client):
    """Verify live calculation of Total, Pending, In Progress, and Resolved counts."""
    # Login as admin
    client.post("/admin/login", data={"username": "admin", "password": "adminpassword123"})

    # Add 3 complaints
    c1 = client.post("/api/complaints", data={
        "student_name": "User 1", "student_email": "u1@campus.edu", "title": "Issue 1",
        "category": "Hostel", "priority": "Low", "location": "H1", "description": "Desc 1"
    }).get_json()["complaint_id"]

    c2 = client.post("/api/complaints", data={
        "student_name": "User 2", "student_email": "u2@campus.edu", "title": "Issue 2",
        "category": "Hostel", "priority": "Medium", "location": "H2", "description": "Desc 2"
    }).get_json()["complaint_id"]

    c3 = client.post("/api/complaints", data={
        "student_name": "User 3", "student_email": "u3@campus.edu", "title": "Issue 3",
        "category": "Hostel", "priority": "High", "location": "H3", "description": "Desc 3"
    }).get_json()["complaint_id"]

    # Transition c2 to 'In Progress' and c3 to 'Resolved'
    client.post(f"/api/complaints/{c2}/status", json={"status": "In Progress"})
    client.post(f"/api/complaints/{c3}/status", json={"status": "Resolved"})

    stats_res = client.get("/api/complaints/statistics")
    assert stats_res.status_code == 200
    stats = stats_res.get_json()["statistics"]

    assert stats["total"] == 3
    assert stats["pending"] == 1
    assert stats["in_progress"] == 1
    assert stats["resolved"] == 1


# ==============================================================================
# 9. Database Error Handling
# ==============================================================================

def test_database_error_handling(client):
    """Verify graceful error responses on nonexistent records and bad payloads."""
    # Login as admin
    client.post("/admin/login", data={"username": "admin", "password": "adminpassword123"})

    # Update non-existent complaint
    res = client.post("/api/complaints/CMP-NONEXISTENT/status", json={"status": "Resolved"})
    assert res.status_code == 404
    assert res.get_json()["success"] is False

    # Empty payload to status update
    bad_payload_res = client.post("/api/complaints/CMP-NONEXISTENT/status", json={})
    assert bad_payload_res.status_code == 400


# ==============================================================================
# 10. Amazon SNS Notification Integration Tests
# ==============================================================================

def test_sns_notification_triggers_on_status_update(client, monkeypatch):
    """Verify that updating a complaint triggers an Amazon SNS notification."""
    published_messages = []

    class MockSNSClient:
        def publish(self, **kwargs):
            published_messages.append(kwargs)
            return {"MessageId": "mock-sns-msg-12345"}

    import app as app_module
    monkeypatch.setattr(app_module, "SNS_TOPIC_ARN", "arn:aws:sns:us-east-1:123456789012:test-topic")
    monkeypatch.setattr(app_module, "get_sns_client", lambda: MockSNSClient())

    # Create complaint
    create_res = client.post("/api/complaints", data={
        "student_name": "Test Student",
        "student_email": "student@campus.edu",
        "title": "Air Conditioner Leaking",
        "category": "Classroom Equipment",
        "priority": "High",
        "location": "LH-101",
        "description": "Water leaking on front row desks."
    })
    tracking_id = create_res.get_json()["complaint_id"]

    # One SNS alert for new submission
    assert len(published_messages) == 1
    assert "Air Conditioner Leaking" in published_messages[0]["Message"]

    # Login as admin and update status
    client.post("/admin/login", data={"username": "admin", "password": "adminpassword123"})
    update_res = client.post(f"/api/complaints/{tracking_id}/status", json={
        "status": "Resolved",
        "remarks": "Replaced AC drainage pipe."
    })
    assert update_res.status_code == 200

    # Second SNS alert for status update
    assert len(published_messages) == 2
    assert "RESOLVED" in published_messages[1]["Message"]
    assert "Replaced AC drainage pipe" in published_messages[1]["Message"]

