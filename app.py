import os
import re
import uuid
from functools import wraps
from flask import (
    Flask, render_template, request, jsonify,
    session, redirect, url_for, send_from_directory
)
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import database

# Load environment configuration
load_dotenv()

app = Flask(__name__)

# Security and session configuration
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "smart-campus-dev-secret-key-change-in-production"
)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["MAX_CONTENT_LENGTH"] = int(
    os.environ.get("MAX_CONTENT_LENGTH", 5 * 1024 * 1024)
)
app.config["UPLOAD_FOLDER"] = os.environ.get("UPLOAD_FOLDER", "uploads")
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", "smart-campus-complaints-br2026x7")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
ALLOWED_STATUSES = {"Pending", "In Progress", "Resolved"}
ALLOWED_CATEGORIES = {
    "Electrical", "Wi-Fi / Internet", "Classroom Equipment",
    "Plumbing", "Hostel", "Cleanliness", "Other"
}
ALLOWED_PRIORITIES = {"Low", "Medium", "High"}
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN", "")

# Ensure local upload directory exists for fallback
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Initialize database schema and default admin
database.init_db()
database.seed_default_admin()


def get_s3_client():
    """Return boto3 S3 client using EC2 IAM Role (no hardcoded keys)."""
    try:
        import boto3
        return boto3.client("s3", region_name=AWS_REGION)
    except Exception:
        return None


def get_sns_client():
    """Return boto3 SNS client using EC2 IAM Role (no hardcoded keys)."""
    try:
        import boto3
        return boto3.client("sns", region_name=AWS_REGION)
    except Exception:
        return None


def publish_status_update_notification(tracking_id, title, new_status, remarks, student_name, student_email):
    """Publish an automated status update notification to Amazon SNS topic."""
    if not SNS_TOPIC_ARN:
        return False
    try:
        sns = get_sns_client()
        if not sns:
            return False

        subject = f"[Smart Campus] Update: {tracking_id} is now {new_status}"[:100]
        body = (
            f"Dear {student_name or 'Student'},\n\n"
            f"Your campus complaint status has been updated.\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Tracking ID  : {tracking_id}\n"
            f"Title        : {title}\n"
            f"New Status   : {new_status.upper()}\n"
            f"Admin Remarks: {remarks or 'No remarks provided'}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"You can track this complaint anytime on the student portal.\n\n"
            f"-- Smart Campus HelpDesk Notification Service (AWS EC2 + SNS)"
        )
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject,
            Message=body
        )
        return True
    except Exception as e:
        app.logger.warning(f"SNS status update publish skipped or failed: {e}")
        return False


def publish_new_complaint_notification(tracking_id, title, category, priority, location, student_name):
    """Publish an automated alert to Amazon SNS topic when a new complaint is filed."""
    if not SNS_TOPIC_ARN:
        return False
    try:
        sns = get_sns_client()
        if not sns:
            return False

        subject = f"[Smart Campus Alert] New {priority} Priority Complaint: {tracking_id}"[:100]
        body = (
            f"New student complaint submitted to Smart Campus HelpDesk:\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Tracking ID : {tracking_id}\n"
            f"Category    : {category}\n"
            f"Priority    : {priority}\n"
            f"Location    : {location}\n"
            f"Title       : {title}\n"
            f"Submitted By: {student_name}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Log into the Admin Dashboard to review and assign maintenance staff.\n\n"
            f"-- Smart Campus HelpDesk Notification Service (AWS EC2 + SNS)"
        )
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject,
            Message=body
        )
        return True
    except Exception as e:
        app.logger.warning(f"SNS new complaint publish skipped or failed: {e}")
        return False


def allowed_file(filename):
    """Check if uploaded file has an approved image extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def admin_required(f):
    """Decorator to enforce administrator authentication on sensitive endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin_logged_in"):
            if request.path.startswith("/api/"):
                return jsonify({
                    "success": False,
                    "message": "Administrator authentication required."
                }), 401
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated_function


# ==============================================================================
# Public Frontend Routes
# ==============================================================================

@app.route("/")
def home():
    """Campus portal landing page."""
    return render_template("index.html")


@app.route("/complaint")
def complaint():
    """Complaint submission page."""
    return render_template("complaint.html")


@app.route("/track")
def track():
    """Complaint tracking search page."""
    return render_template("track.html")


@app.route("/health")
def health():
    """Health check endpoint for AWS Load Balancer or monitoring."""
    return jsonify({
        "status": "ok",
        "service": "smart-campus-helpdesk",
        "database": "Amazon RDS MySQL" if database.is_rds() else "SQLite Local",
        "storage": "Amazon S3" if S3_BUCKET_NAME else "Local Disk",
        "notifications": "Amazon SNS" if SNS_TOPIC_ARN else "Configurable (Amazon SNS)"
    }), 200


# ==============================================================================
# Public Complaint Submission & Tracking APIs
# ==============================================================================

@app.route("/api/complaints", methods=["POST"])
def submit_complaint():
    """
    Handle student complaint submissions.
    Validates form data, streams optional image attachments directly to Amazon S3,
    and returns a unique tracking ID.
    """
    try:
        data = request.form

        # Extract and validate required student fields
        student_name = data.get("student_name", "").strip()
        student_email = data.get("student_email", "").strip()
        title = data.get("title", "").strip()
        category = data.get("category", "").strip()
        priority = data.get("priority", "").strip()
        location = data.get("location", "").strip()
        description = data.get("description", "").strip()

        # Input validation checks
        if not student_name or len(student_name) > 100:
            return jsonify({"success": False, "message": "Full Name is required (max 100 chars)."}), 400

        email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        if not student_email or len(student_email) > 254 or not re.match(email_pattern, student_email):
            return jsonify({"success": False, "message": "A valid email address is required."}), 400

        if not title or len(title) > 150:
            return jsonify({"success": False, "message": "Title is required (max 150 chars)."}), 400

        if category not in ALLOWED_CATEGORIES:
            return jsonify({"success": False, "message": "Invalid category selected."}), 400

        if priority not in ALLOWED_PRIORITIES:
            return jsonify({"success": False, "message": "Invalid priority selected."}), 400

        if not location or len(location) > 200:
            return jsonify({"success": False, "message": "Campus location is required (max 200 chars)."}), 400

        if not description or len(description) > 3000:
            return jsonify({"success": False, "message": "Description is required (max 3000 chars)."}), 400

        # Handle optional image attachment: Upload to Amazon S3
        image_filename = None
        if "image" in request.files:
            file = request.files["image"]
            if file and file.filename != "":
                if not allowed_file(file.filename):
                    return jsonify({
                        "success": False,
                        "message": "Only JPG, PNG, or WebP images are allowed."
                    }), 400

                safe_name = secure_filename(file.filename)
                unique_name = f"{uuid.uuid4().hex}_{safe_name}"
                s3_key = f"complaints/{unique_name}"

                s3 = get_s3_client()
                uploaded_to_s3 = False

                if s3 and S3_BUCKET_NAME:
                    try:
                        s3.upload_fileobj(
                            file,
                            S3_BUCKET_NAME,
                            s3_key,
                            ExtraArgs={"ContentType": file.content_type or "image/jpeg"}
                        )
                        image_filename = s3_key
                        uploaded_to_s3 = True
                    except Exception as s3_err:
                        app.logger.warning(f"S3 upload failed, falling back to local storage: {s3_err}")

                if not uploaded_to_s3:
                    file.seek(0)
                    local_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
                    file.save(local_path)
                    image_filename = unique_name

        # Insert complaint into database (Amazon RDS or SQLite)
        complaint_payload = {
            "student_name": student_name,
            "student_email": student_email,
            "title": title,
            "category": category,
            "priority": priority,
            "location": location,
            "description": description,
            "image_filename": image_filename
        }

        tracking_id = database.create_complaint(complaint_payload)

        # Dispatch automated SNS notification for new complaint submission
        publish_new_complaint_notification(
            tracking_id=tracking_id,
            title=title,
            category=category,
            priority=priority,
            location=location,
            student_name=student_name
        )

        return jsonify({
            "success": True,
            "message": "Complaint submitted successfully.",
            "complaint_id": tracking_id
        }), 201

    except Exception as e:
        app.logger.error(f"Error submitting complaint: {e}")
        return jsonify({
            "success": False,
            "message": "Failed to process complaint due to a server error."
        }), 500


@app.route("/api/complaints/<tracking_id>", methods=["GET"])
def get_complaint_status(tracking_id):
    """
    Public tracking lookup endpoint.
    Returns non-sensitive complaint details and current status.
    """
    clean_id = tracking_id.strip()
    complaint_data = database.get_complaint_by_tracking_id(clean_id)

    if not complaint_data:
        return jsonify({
            "success": False,
            "message": f"No complaint found matching ID '{clean_id}'."
        }), 404

    return jsonify({
        "success": True,
        "complaint": complaint_data
    }), 200


@app.route("/api/complaints/<tracking_id>/image", methods=["GET"])
def get_complaint_image(tracking_id):
    """
    Generate a secure pre-signed Amazon S3 URL to view complaint evidence photo.
    """
    clean_id = tracking_id.strip()
    complaint_data = database.get_complaint_by_tracking_id(clean_id)

    if not complaint_data or not complaint_data.get("image_filename"):
        return jsonify({"success": False, "message": "No image attachment found."}), 404

    image_key = complaint_data["image_filename"]

    # If stored in Amazon S3, generate secure pre-signed URL (expires in 1 hour)
    if image_key.startswith("complaints/"):
        s3 = get_s3_client()
        if s3 and S3_BUCKET_NAME:
            try:
                presigned_url = s3.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": S3_BUCKET_NAME, "Key": image_key},
                    ExpiresIn=3600
                )
                return redirect(presigned_url)
            except Exception as e:
                app.logger.error(f"Failed to generate S3 pre-signed URL: {e}")

    # Fallback to local uploads directory
    filename = os.path.basename(image_key)
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# ==============================================================================
# Admin Authentication & Management Routes
# ==============================================================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """Administrator login page and credential verification."""
    if session.get("admin_logged_in"):
        return redirect(url_for("admin_dashboard"))

    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if database.verify_admin_credentials(username, password):
            session.clear()
            session["admin_logged_in"] = True
            session["admin_user"] = username
            return redirect(url_for("admin_dashboard"))
        else:
            error = "Invalid administrator username or password."

    return render_template("login.html", error=error)


@app.route("/admin/logout", methods=["GET", "POST"])
def admin_logout():
    """Clear administrator session and return to home page."""
    session.clear()
    return redirect(url_for("home"))


@app.route("/admin")
@admin_required
def admin_dashboard():
    """Render protected administrator dashboard."""
    return render_template("admin.html")


@app.route("/api/complaints", methods=["GET"])
@admin_required
def list_admin_complaints():
    """Fetch all complaints from Amazon RDS / SQLite for the admin dashboard."""
    try:
        complaints_list = database.get_all_complaints()
        return jsonify({
            "success": True,
            "complaints": complaints_list
        }), 200
    except Exception as e:
        app.logger.error(f"Error fetching complaints: {e}")
        return jsonify({
            "success": False,
            "message": "Error loading complaints from database."
        }), 500


@app.route("/api/complaints/statistics", methods=["GET"])
@admin_required
def complaint_statistics():
    """Return live summary counts (Total, Pending, In Progress, Resolved)."""
    try:
        stats = database.get_complaint_statistics()
        return jsonify({
            "success": True,
            "statistics": stats
        }), 200
    except Exception as e:
        app.logger.error(f"Error calculating stats: {e}")
        return jsonify({
            "success": False,
            "message": "Error calculating complaint statistics."
        }), 500


@app.route("/api/complaints/<tracking_id>/status", methods=["POST"])
@admin_required
def update_status(tracking_id):
    """
    Update complaint status and record audit log in history table.
    """
    clean_id = tracking_id.strip()
    payload = request.get_json(silent=True) or request.form

    new_status = payload.get("status")
    remarks = payload.get("remarks", f"Status changed to {new_status}")
    admin_user = session.get("admin_user", "Admin")

    if not new_status or new_status not in ALLOWED_STATUSES:
        return jsonify({
            "success": False,
            "message": f"Invalid status. Must be one of: {list(ALLOWED_STATUSES)}"
        }), 400

    try:
        # Retrieve existing complaint details for notification
        existing = database.get_complaint_by_tracking_id(clean_id)

        updated = database.update_complaint_status(
            clean_id, new_status, remarks=remarks, changed_by=admin_user
        )

        if not updated:
            return jsonify({
                "success": False,
                "message": f"Complaint '{clean_id}' not found."
            }), 404

        # Dispatch automated SNS email notification
        if existing:
            publish_status_update_notification(
                tracking_id=clean_id,
                title=existing.get("title", "Campus Grievance"),
                new_status=new_status,
                remarks=remarks,
                student_name=existing.get("student_name", "Student"),
                student_email=existing.get("student_email", "")
            )

        return jsonify({
            "success": True,
            "message": f"Complaint {clean_id} updated to {new_status}.",
            "status": new_status
        }), 200

    except Exception as e:
        app.logger.error(f"Error updating status: {e}")
        return jsonify({
            "success": False,
            "message": "Failed to update complaint status in database."
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
