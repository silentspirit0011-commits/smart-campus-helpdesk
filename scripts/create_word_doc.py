import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, hex_color):
    """Set background color of a table cell."""
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tc_pr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set cell padding."""
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tc_pr.append(tc_mar)

def add_styled_heading(doc, text, level):
    """Add a heading with tailored styling."""
    h = doc.add_heading(text, level=level)
    h.paragraph_format.keep_with_next = True
    h.paragraph_format.space_before = Pt(14)
    h.paragraph_format.space_after = Pt(6)
    run = h.runs[0]
    if level == 1:
        run.font.color.rgb = RGBColor(15, 23, 42)  # Navy / Slate 900
        run.font.size = Pt(16)
        run.bold = True
    elif level == 2:
        run.font.color.rgb = RGBColor(30, 58, 138)  # Deep Blue
        run.font.size = Pt(13)
        run.bold = True
    elif level == 3:
        run.font.color.rgb = RGBColor(55, 65, 81)   # Slate 700
        run.font.size = Pt(11)
        run.bold = True
    return h

def add_code_block(doc, code_text):
    """Add a monospace shaded code block."""
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    cell = table.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, "F1F5F9")
    set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
    
    # Border
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>'
        f'<w:left w:val="single" w:sz="18" w:space="0" w:color="2563EB"/>'
        f'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>'
        f'<w:right w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>'
        f'</w:tcBorders>'
    )
    tc_pr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(code_text.strip())
    run.font.name = "Consolas"
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(30, 41, 59)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def format_table(table, header_bg="1E3A8A", alt_bg="F8FAFC"):
    """Format table with styled header and alternating row shading."""
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    # Format header
    for cell in table.rows[0].cells:
        set_cell_background(cell, header_bg)
        set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for run in p.runs:
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)
                run.font.size = Pt(9.5)
                
    # Format data rows
    for r_idx, row in enumerate(table.rows[1:], start=1):
        bg = alt_bg if r_idx % 2 == 1 else "FFFFFF"
        for cell in row.cells:
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
            for p in cell.paragraphs:
                for run in p.runs:
                    run.font.size = Pt(9)
                    run.font.color.rgb = RGBColor(30, 41, 59)

def build_word_report():
    doc = Document()
    
    # Set page margins to 0.8 inches
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)
        
    # Document Title Block
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(2)
    t_run = title_p.add_run("Smart Campus HelpDesk & Grievance Redressal System")
    t_run.font.size = Pt(22)
    t_run.font.bold = True
    t_run.font.color.rgb = RGBColor(15, 23, 42)
    
    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_before = Pt(0)
    sub_p.paragraph_format.space_after = Pt(14)
    s_run = sub_p.add_run("Comprehensive Cloud Architecture & Implementation Report")
    s_run.font.size = Pt(13)
    s_run.font.color.rgb = RGBColor(37, 99, 235)
    
    # Metadata Card Table
    meta_table = doc.add_table(rows=5, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Course / Subject:", "Cloud Computing / AWS Cloud Architecture"),
        ("Academic Year:", "2026–2027"),
        ("Architecture Model:", "Decoupled 3-Tier Enterprise Cloud Architecture"),
        ("Primary AWS Region:", "us-east-1 (US East - N. Virginia)"),
        ("Team Responsibilities:", "Member 1: Frontend & UI | Member 2: Backend, AWS Cloud & Database")
    ]
    for i, (k, v) in enumerate(meta_data):
        cell_k, cell_v = meta_table.cell(i, 0), meta_table.cell(i, 1)
        cell_k.width = Inches(2.2)
        cell_v.width = Inches(4.5)
        
        pk = cell_k.paragraphs[0]
        pk.paragraph_format.space_after = Pt(2)
        rk = pk.add_run(k)
        rk.font.bold = True
        rk.font.size = Pt(9.5)
        rk.font.color.rgb = RGBColor(15, 23, 42)
        
        pv = cell_v.paragraphs[0]
        pv.paragraph_format.space_after = Pt(2)
        rv = pv.add_run(v)
        rv.font.size = Pt(9.5)
        rv.font.color.rgb = RGBColor(51, 65, 85)
        
        set_cell_background(cell_k, "F1F5F9")
        set_cell_background(cell_v, "F8FAFC")
        set_cell_margins(cell_k, top=60, bottom=60, left=100, right=100)
        set_cell_margins(cell_v, top=60, bottom=60, left=100, right=100)
        
    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    
    # 1. Executive Summary
    add_styled_heading(doc, "1. Executive Summary", level=1)
    p = doc.add_paragraph(
        "Traditional campus complaint redressal mechanisms rely on physical paper forms, manual emails, or unmanaged spreadsheets. "
        "These methods suffer from lack of accountability, zero tracking visibility, lost attachments, and security vulnerabilities."
    )
    p.paragraph_format.space_after = Pt(6)
    
    p2 = doc.add_paragraph(
        "The Smart Campus HelpDesk is a production-ready, cloud-native web application built to streamline incident reporting, "
        "evidence verification, and administrative resolution. The application is architected around a stateless, decoupled 3-tier model "
        "deployed across Amazon Web Services (AWS):"
    )
    p2.paragraph_format.space_after = Pt(4)
    
    points = [
        ("Presentation Layer: ", "Modern, mobile-responsive web portal (HTML5, CSS3, Vanilla JavaScript) enabling students to file grievances, upload photographic evidence, and track status via unique tracking IDs."),
        ("Application / Compute Layer: ", "Python 3 Flask RESTful API hosted on Amazon EC2 (t2.micro) running Amazon Linux 2023, managed as a resilient background daemon via Linux systemd."),
        ("Managed Data & Storage Layer: ", "Relational records and audit logs persist in Amazon RDS MySQL, while complaint evidence photos are stored in Amazon S3 with time-limited cryptographic Pre-Signed URLs."),
        ("Monitoring & Alerting Layer: ", "Infrastructure health is tracked using Amazon CloudWatch, triggering real-time incident email alerts via Amazon SNS.")
    ]
    for b_title, b_desc in points:
        bp = doc.add_paragraph(style='List Bullet')
        bp.paragraph_format.space_after = Pt(3)
        rt = bp.add_run(b_title)
        rt.bold = True
        rt.font.color.rgb = RGBColor(30, 58, 138)
        bp.add_run(b_desc)

    # 2. Faculty Rubric Compliance Matrix
    add_styled_heading(doc, "2. Faculty Rubric Compliance Matrix", level=1)
    
    rubric_rows = [
        ("#", "Faculty Rubric Requirement", "Project Implementation & Technical Proof", "Status"),
        ("1", "Working Cloud App with Frontend, Backend & Database", "Full-stack application with client UI, Flask REST API, and Amazon RDS MySQL. Verified with 11/11 automated unit tests.", "MET"),
        ("2", "Main Backend on EC2 / Compute (No pure serverless)", "Core REST API and backend run on Amazon EC2 t2.micro (i-05c6a91b47a153e81) managed by systemd.", "MET"),
        ("3", "Custom VPC with Subnets, Route Tables, IGW & SGs", "Deployed in custom VPC (vpc-08e22f2b09341874a) with isolated subnets, IGW, and multi-tier Security Groups.", "MET"),
        ("4", "Managed Database: Amazon RDS", "Amazon RDS MySQL (campus-complaints-db) with foreign keys, transactional integrity, and autocommit.", "MET"),
        ("5", "Amazon S3 for Genuine Requirement", "Amazon S3 Bucket (smart-campus-complaints-br2026x7) storing complaint photos, served via AWS Pre-Signed URLs.", "MET"),
        ("6", "IAM Least Privilege & No Hardcoded Keys", "EC2 uses IAM Instance Profile (boto3 S3 and SNS). Zero AWS access keys or secrets in code or repository.", "MET"),
        ("7", "Sensitive Config Stored Securely", "Database passwords, secret keys, and AWS configurations loaded via .env environment variables.", "MET"),
        ("8", "CloudWatch Monitoring & at least 1 Alarm", "CloudWatch Alarm SmartCampus-HighCPU-Alarm monitoring EC2 CPUUtilization > 80% in us-east-1.", "MET"),
        ("9", "AWS Cloud Budget & Cost Alert", "Configured $1.00 Monthly Zero-Spend Budget in AWS Budgets with 80% threshold email notifications.", "MET"),
        ("10", "Integrate at least 5 Cloud Services", "7 Services Integrated: EC2, RDS MySQL, S3, VPC, IAM, CloudWatch, and SNS.", "EXCEEDS (7/5)"),
        ("11", "At least 2 Additional Cloud Capabilities", "Implemented Amazon SNS notifications, CloudWatch alarms, S3 Pre-Signed URLs, and audit trail logging.", "EXCEEDS (4/2)"),
        ("12", "Serverless as Supporting Components Only", "S3 and SNS act purely as auxiliary storage/messaging components; EC2 hosts the core business logic.", "MET"),
        ("13", "Clear Functional Purpose for Every Service", "Every service directly solves an architectural problem (Compute, DB, Storage, Security, Alerts). No unused services.", "MET"),
        ("14", "Non-Trivial Project (Not Static or Basic CRUD)", "Full grievance state machine (Pending -> In Progress -> Resolved), tracking IDs (CMP-XXXXXXXX), and RBAC.", "MET"),
        ("15", "Demonstrates 5 Cloud Areas", "1. Compute, 2. Networking, 3. Database, 4. Storage, 5. Security/IAM, 6. Monitoring.", "EXCEEDS (6/5)"),
        ("16", "Free Tier Compliance & Cost Avoidance", "Single-AZ t2.micro EC2, db.t3.micro RDS, no expensive NAT Gateways ($32/mo) or multi-AZ overhead.", "MET")
    ]
    
    r_table = doc.add_table(rows=len(rubric_rows), cols=4)
    col_widths = [Inches(0.4), Inches(2.2), Inches(3.2), Inches(0.9)]
    for r_idx, row in enumerate(rubric_rows):
        for c_idx, val in enumerate(row):
            cell = r_table.cell(r_idx, c_idx)
            cell.width = col_widths[c_idx]
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run(val)
            if c_idx == 3 and r_idx > 0:
                run.bold = True
                run.font.color.rgb = RGBColor(16, 149, 193) if "EXCEEDS" in val else RGBColor(22, 101, 52)
    format_table(r_table)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # 3. Cloud Architecture & System Design
    add_styled_heading(doc, "3. Cloud Architecture & System Design", level=1)
    doc.add_paragraph(
        "The architecture follows a decoupled 3-tier design ensuring that compute, storage, and database layers scale independently. "
        "The EC2 instance is completely stateless: if the instance terminates, all database records remain safe in Amazon RDS MySQL, "
        "and all photographic evidence remains durable in Amazon S3."
    )
    
    add_code_block(doc, 
"""+----------------------------------------------------------------------------------------------------+
|                                    AMAZON VPC (vpc-08e22f2b09341874a)                              |
|                                                                                                    |
|  [ Internet Gateway ] <---> [ Elastic IP: Static IPv4 ] <---> [ Security Group: smart-campus-ec2-sg ]
|                                                                     |                              |
|   +-------------------------------------------------------------+   | (Port 80 / 5000 / 22)        |
|   | Public Subnet (10.0.6.0/24)                                 |   v                              |
|   |  - Amazon EC2 Instance (smart-campus-ec2 / t2.micro)        |<--+                              |
|   |  - Linux systemd Daemon (smart-campus.service)              |                                  |
|   |  - Python Flask REST API & Web Server (app.py)              |                                  |
|   |  - IAM Instance Profile Attached (No hardcoded keys)        |                                  |
|   +-------------------------------------------------------------+                                  |
|                                |                              |                                    |
|      (Relational SQL Port 3306)|                              | (Uploads & Pre-Signed URLs)        |
|                                v                              v                                    |
|   +---------------------------------------+       +--------------------------------------------+   |
|   | Database Subnet                       |       | Amazon S3 Object Storage                   |   |
|   |  - Amazon RDS MySQL Instance          |       |  - Bucket: smart-campus-complaints-br2026x7|   |
|   |  - SG: Allows Inbound from EC2 ONLY   |       |  - Private Bucket (SigV4 Pre-Signed URLs)  |   |
|   +---------------------------------------+       +--------------------------------------------+   |
|                                                                                                    |
|   +---------------------------------------+       +--------------------------------------------+   |
|   | Amazon CloudWatch                     |       | Amazon Simple Notification Service (SNS)   |   |
|   |  - Alarm: SmartCampus-HighCPU-Alarm   |------>|  - Topic: smart-campus-notifications       |   |
|   |  - Metric: CPUUtilization > 80%       |       |  - Instant Push Email Alerts to Students   |   |
|   +---------------------------------------+       +--------------------------------------------+   |
+----------------------------------------------------------------------------------------------------+"""
    )

    # 4. AWS Services & Functional Justification
    add_styled_heading(doc, "4. Integrated AWS Services & Technical Justification", level=1)
    services_data = [
        ("#", "AWS Service", "Category", "Architecture Role & Technical Justification"),
        ("1", "Amazon EC2 (t2.micro)", "Compute", "Hosts the Python Flask application and REST API. Provides dedicated virtual compute with persistent execution managed by Linux systemd."),
        ("2", "Amazon RDS MySQL", "Database", "Managed relational database hosting complaints, status histories, and administrator credentials. Offloads automated patching, backups, and point-in-time recovery."),
        ("3", "Amazon S3", "Storage", "Object store providing 99.999999999% (11 9's) durability for student grievance photos and documentation. Keeps EC2 stateless and decoupled."),
        ("4", "Amazon VPC & Security Groups", "Networking", "Enforces perimeter network isolation. Contains public subnet for web ingress and private database subnet. Security Groups ensure MySQL port 3306 is reachable only from EC2."),
        ("5", "AWS Elastic IP (EIP)", "Networking", "Allocates a permanent static IPv4 address. Prevents endpoint disruption across EC2 stop/start cycles."),
        ("6", "AWS IAM", "Security", "Assigns an IAM Instance Profile to EC2, granting scoped permissions to S3 and SNS. Completely eliminates long-term AWS access keys in code."),
        ("7", "Amazon CloudWatch", "Monitoring", "Collects hypervisor-level metrics (CPUUtilization, NetworkIn, DiskReadBytes) and triggers automated alarms when system thresholds are exceeded."),
        ("8", "Amazon SNS", "Messaging", "Decoupled event publishing service dispatching push email alerts to students and staff upon status changes and system alarms.")
    ]
    s_table = doc.add_table(rows=len(services_data), cols=4)
    col_w = [Inches(0.4), Inches(1.8), Inches(1.1), Inches(3.4)]
    for r_idx, row in enumerate(services_data):
        for c_idx, val in enumerate(row):
            cell = s_table.cell(r_idx, c_idx)
            cell.width = col_w[c_idx]
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.add_run(val)
    format_table(s_table)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # 5. Security & Governance
    add_styled_heading(doc, "5. Security, Governance & IAM Policy", level=1)
    doc.add_paragraph(
        "To adhere strictly to AWS security best practices and least-privilege principles, the application does not store "
        "AWS credentials anywhere in source code or configuration files. Instead, the backend retrieves temporary rotating "
        "credentials automatically via the EC2 Instance Metadata Service (IMDSv2)."
    )
    
    add_code_block(doc,
"""{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3EvidenceAttachmentPolicy",
      "Effect": "Allow",
      "Action": ["s3:PutObject", "s3:GetObject", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::smart-campus-complaints-br2026x7",
        "arn:aws:s3:::smart-campus-complaints-br2026x7/*"
      ]
    },
    {
      "Sid": "SNSEmailNotificationPolicy",
      "Effect": "Allow",
      "Action": ["sns:Publish"],
      "Resource": "arn:aws:sns:us-east-1:*:smart-campus-notifications"
    }
  ]
}"""
    )

    # 6. Cost Optimization & Free Tier Breakdown
    add_styled_heading(doc, "6. Cost Optimization & AWS Free Tier Compliance", level=1)
    cost_rows = [
        ("AWS Service Component", "Allocated Sizing", "Monthly Usage", "Free Tier Allowance", "Net Cost"),
        ("Amazon EC2 Compute", "t2.micro (1 vCPU, 1 GB RAM)", "730 Hours", "750 Hours / Month", "$0.00"),
        ("Amazon RDS Database", "db.t3.micro Single-AZ (20 GB gp2)", "730 Hours", "750 Hours / Month", "$0.00"),
        ("Amazon S3 Object Storage", "Standard Storage Tier", "< 1 GB", "5.0 GB / Month", "$0.00"),
        ("Internet Gateway Data Egress", "Outbound Network Transfer", "< 5 GB", "100 GB / Month", "$0.00"),
        ("Amazon CloudWatch Alarms", "1 Metric Alarm (High CPU)", "1 Alarm", "10 Standard Alarms Free", "$0.00"),
        ("Amazon SNS Notifications", "Push Email Deliveries", "< 500 Emails", "100,000 Emails / Month", "$0.00"),
        ("TOTAL ESTIMATED COST", "", "", "", "$0.00 / Month")
    ]
    c_table = doc.add_table(rows=len(cost_rows), cols=5)
    c_col_w = [Inches(1.8), Inches(1.8), Inches(1.0), Inches(1.2), Inches(0.9)]
    for r_idx, row in enumerate(cost_rows):
        for c_idx, val in enumerate(row):
            cell = c_table.cell(r_idx, c_idx)
            cell.width = c_col_w[c_idx]
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run(val)
            if r_idx == len(cost_rows) - 1:
                run.bold = True
                run.font.color.rgb = RGBColor(22, 101, 52)
    format_table(c_table)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # 7. REST API Documentation
    add_styled_heading(doc, "7. Application REST API Endpoints", level=1)
    api_rows = [
        ("HTTP Method", "Route Endpoint", "Access", "Functionality & Integration"),
        ("GET", "/", "Public", "Campus HelpDesk landing page and navigation hub"),
        ("GET", "/complaint", "Public", "Student grievance submission form with photo upload"),
        ("GET", "/track", "Public", "Grievance status lookup and timeline search interface"),
        ("GET", "/health", "Public", "Live cloud service healthcheck (Amazon RDS + S3 + SNS)"),
        ("POST", "/api/complaints", "Public", "Submits complaint, uploads image to S3, returns tracking ID"),
        ("GET", "/api/complaints/<id>", "Public", "Fetches non-sensitive complaint details and status history"),
        ("GET", "/api/complaints/<id>/image", "Admin", "Generates expiring S3 Pre-Signed URL for evidence inspection"),
        ("POST", "/admin/login", "Public", "Authenticates administrator session using PBKDF2 hash"),
        ("GET", "/admin", "Admin", "Protected Administrator Management Dashboard"),
        ("GET", "/api/complaints", "Admin", "Lists all complaints from Amazon RDS MySQL for admin table"),
        ("GET", "/api/complaints/statistics", "Admin", "Calculates live metrics (Total, Pending, Progress, Resolved)"),
        ("POST", "/api/complaints/<id>/status", "Admin", "Updates status, records audit log, triggers Amazon SNS email")
    ]
    a_table = doc.add_table(rows=len(api_rows), cols=4)
    a_col_w = [Inches(1.0), Inches(2.0), Inches(0.8), Inches(2.9)]
    for r_idx, row in enumerate(api_rows):
        for c_idx, val in enumerate(row):
            cell = a_table.cell(r_idx, c_idx)
            cell.width = a_col_w[c_idx]
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run(val)
            if c_idx == 0 and r_idx > 0:
                run.bold = True
                run.font.color.rgb = RGBColor(37, 99, 235)
    format_table(a_table)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # 8. Screenshots & Evidence Checklist
    add_styled_heading(doc, "8. Demonstration Evidence & Screenshots Checklist", level=1)
    doc.add_paragraph(
        "The following screenshots provide verified evidence of working cloud infrastructure for faculty evaluation:"
    )
    
    checks = [
        "Screenshot 1: Portal Landing Page (http://<ELASTIC_IP>/)",
        "Screenshot 2: Student Grievance Submission with Image Attachment (/complaint)",
        "Screenshot 3: Public Grievance Tracking Timeline showing 'Resolved' Status (/track)",
        "Screenshot 4: Protected Administrator Dashboard with Analytics & Table (/admin)",
        "Screenshot 5: AWS EC2 Management Console showing 'smart-campus-ec2' and Elastic IP",
        "Screenshot 6: AWS RDS Management Console showing 'campus-complaints-db' in Available State",
        "Screenshot 7: AWS S3 Management Console showing uploaded evidence files inside 'complaints/'",
        "Screenshot 8: AWS CloudWatch Console showing 'SmartCampus-HighCPU-Alarm' in OK State",
        "Screenshot 9: AWS Budgets Dashboard showing the $1.00 Monthly Free-Tier Cost Budget",
        "Screenshot 10: Email Inbox showing Automated Push Notification delivered via Amazon SNS"
    ]
    for chk in checks:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(3)
        run = p.add_run(chk)
        run.font.color.rgb = RGBColor(51, 65, 85)
        
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # 9. Viva & Technical Defense
    add_styled_heading(doc, "9. Viva Voce & Technical Defense Q&A", level=1)
    
    viva_qa = [
        ("Q1: Why is this project not just a 'single EC2 webpage' or 'basic CRUD'?",
         "A single EC2 webpage is a monolith where code, database files, and uploaded images reside on the same server disk. If that EC2 instance is terminated, 100% of data is permanently lost. Our system implements a decoupled 3-tier architecture: the EC2 server is completely stateless. Relational records reside independently in Amazon RDS with foreign-key constraints and audit history, while files reside in Amazon S3 with 11 9's durability. Terminating our EC2 instance results in zero data loss."),
        ("Q2: How are AWS credentials protected in application code?",
         "We follow the principle of least privilege using an IAM Instance Profile attached directly to EC2. The AWS SDK (boto3) retrieves temporary rotating security credentials from the EC2 Instance Metadata Service (IMDSv2). No AWS_ACCESS_KEY_ID or secret keys exist in the repository or configuration files."),
        ("Q3: Why did you use Amazon RDS instead of SQLite?",
         "SQLite locks the database file during writes, cannot scale horizontally, and couples data to the local disk. Amazon RDS provides a managed, enterprise-grade MySQL database engine with automated point-in-time snapshots, automated OS patching, multi-AZ failover capability, and independent scaling from the compute layer."),
        ("Q4: How does your application protect uploaded student images?",
         "The Amazon S3 bucket is completely private; public access is blocked. When an authorized administrator needs to inspect evidence, the backend requests an AWS Signature Version 4 Pre-Signed URL with a 60-minute expiration. Once expired, the URL becomes invalid, preventing unauthorized hotlinking or data exposure."),
        ("Q5: How did you ensure this architecture stayed within Free Tier limits?",
         "We avoided expensive managed services like NAT Gateways (~$32/mo) and multi-AZ deployments. Compute runs on a single t2.micro instance (750 hours free/mo), database runs on db.t3.micro Single-AZ (750 hours free/mo), and storage is within the 5 GB S3 tier. Furthermore, an AWS Budget cost alert is configured at $1.00 to prevent billing surprises.")
    ]
    
    for q, a in viva_qa:
        qp = doc.add_paragraph()
        qp.paragraph_format.space_before = Pt(8)
        qp.paragraph_format.space_after = Pt(2)
        q_run = qp.add_run(q)
        q_run.bold = True
        q_run.font.size = Pt(10.5)
        q_run.font.color.rgb = RGBColor(30, 58, 138)
        
        ap = doc.add_paragraph()
        ap.paragraph_format.space_before = Pt(0)
        ap.paragraph_format.space_after = Pt(6)
        a_run = ap.add_run(a)
        a_run.font.size = Pt(9.5)
        a_run.font.color.rgb = RGBColor(51, 65, 85)

    # Save Document
    output_path = os.path.abspath("docs/PROJECT_REPORT.docx")
    doc.save(output_path)
    print(f"Successfully generated Word document at: {output_path}")

if __name__ == "__main__":
    build_word_report()
