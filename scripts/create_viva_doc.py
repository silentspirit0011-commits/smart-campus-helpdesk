import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def set_cell_background(cell, hex_color):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tc_pr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
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
    h = doc.add_heading(text, level=level)
    h.paragraph_format.keep_with_next = True
    h.paragraph_format.space_before = Pt(14)
    h.paragraph_format.space_after = Pt(6)
    run = h.runs[0]
    if level == 1:
        run.font.color.rgb = RGBColor(15, 23, 42)
        run.font.size = Pt(16)
        run.bold = True
    elif level == 2:
        run.font.color.rgb = RGBColor(30, 58, 138)
        run.font.size = Pt(13)
        run.bold = True
    return h

def format_table(table, header_bg="1E3A8A", alt_bg="F8FAFC"):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for cell in table.rows[0].cells:
        set_cell_background(cell, header_bg)
        set_cell_margins(cell, top=120, bottom=120, left=120, right=120)
        for p in cell.paragraphs:
            for run in p.runs:
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)
                run.font.size = Pt(9.5)
                
    for r_idx, row in enumerate(table.rows[1:], start=1):
        bg = alt_bg if r_idx % 2 == 1 else "FFFFFF"
        for cell in row.cells:
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
            for p in cell.paragraphs:
                for run in p.runs:
                    run.font.size = Pt(9)
                    run.font.color.rgb = RGBColor(30, 41, 59)

def build_viva_doc():
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(0.8)
        s.right_margin = Inches(0.8)
        
    # Title
    tp = doc.add_paragraph()
    tp.paragraph_format.space_after = Pt(2)
    tr = tp.add_run("Smart Campus HelpDesk: Complete Viva Defense & Faculty Rubric Guide")
    tr.font.size = Pt(20)
    tr.font.bold = True
    tr.font.color.rgb = RGBColor(15, 23, 42)
    
    sp = doc.add_paragraph()
    sp.paragraph_format.space_after = Pt(12)
    sr = sp.add_run("Master Service Architecture, Rubric Verification & Top 10 Faculty Defense Answers")
    sr.font.size = Pt(12)
    sr.font.color.rgb = RGBColor(37, 99, 235)
    
    # 1. Master Components Table
    add_styled_heading(doc, "1. Master Service Architecture (Frontend to Cloud Infrastructure)", level=1)
    
    components = [
        ("#", "Service / Component", "Identifier", "Tier", "What It Does", "How It Works Technically (For Viva)"),
        ("1", "Web Frontend UI", "templates/*.html", "Presentation", "User interface for complaints & admin.", "Built with HTML5, CSS3, and Vanilla JS; interacts asynchronously via REST fetch() APIs."),
        ("2", "Flask REST API", "app.py, database.py", "Application", "Business logic, token generation, auth.", "Python 3 WSGI microservice; handles input validation, sessions, and AWS SDK (boto3) calls."),
        ("3", "Amazon EC2", "smart-campus-ec2 (t2.micro)", "Compute", "Runs Python/Flask web app 24/7.", "Virtual compute instance running Amazon Linux 2023 governed by a systemd daemon."),
        ("4", "AWS Elastic IP", "44.219.13.156", "Networking", "Permanent static public IPv4 address.", "Binds a fixed IPv4 to EC2 ENI, preventing endpoint disruption across stop/starts."),
        ("5", "Custom Amazon VPC", "vpc-08e22f2b09341874a", "Networking", "Perimeter cloud network isolation.", "Isolated Public Subnet (10.0.6.0/24) for web ingress & Private Subnet for database tier."),
        ("6", "Security Groups", "smart-campus-ec2-sg & RDS SG", "Security", "Stateful firewall packet filters.", "EC2 allows 80, 5000, 22. RDS SG strictly allows 3306 ONLY from EC2 Security Group."),
        ("7", "Amazon RDS MySQL", "campus-complaints-db (Port 3306)", "Database", "Relational database for complaints.", "Managed MySQL engine handling relational integrity, backups, and parameterized SQL (%s)."),
        ("8", "Amazon S3", "smart-campus-complaints-br2026x7", "Storage", "Durable storage for evidence photos.", "11 9's durability object store; bucket is private; files saved via streaming upload."),
        ("9", "S3 Pre-Signed URLs", "AWS Signature Version 4", "Storage Sec", "Temporary expiring access to photos.", "Backend requests temporary cryptographic URL (expires in 60 mins) to view evidence."),
        ("10", "AWS IAM Role", "EC2 Instance Profile", "Identity", "Zero-credential AWS authorization.", "Uses IMDSv2 to fetch rotating STS tokens. No AWS keys exist in code or repository."),
        ("11", "CloudWatch Alarm", "SmartCampus-HighCPU-Alarm", "Monitoring", "Proactive infrastructure monitoring.", "Monitors CPUUtilization > 80% for 2 periods; changes state to ALARM on spikes."),
        ("12", "Amazon SNS", "smart-campus-notifications", "Messaging", "Real-time push email alerts.", "Pub/sub event broker; pushes instant emails upon status updates and CPU alarms."),
        ("13", "AWS Budgets", "SmartCampus-FreeTier-Budget", "Cost Gov", "Guarantees Free Tier cost protection.", "Monitors billing; Zero-Spend ($1.00) budget with 80% threshold ($0.80) email alert.")
    ]
    
    t1 = doc.add_table(rows=len(components), cols=6)
    widths = [Inches(0.3), Inches(1.3), Inches(1.3), Inches(0.9), Inches(1.3), Inches(1.8)]
    for r_idx, row in enumerate(components):
        for c_idx, val in enumerate(row):
            cell = t1.cell(r_idx, c_idx)
            cell.width = widths[c_idx]
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.add_run(val)
    format_table(t1)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    
    # 2. Rubric Matching Table
    add_styled_heading(doc, "2. Faculty Rubric Matching & Technical Proof", level=1)
    rubric = [
        ("#", "Faculty Rubric Requirement", "How We Met It in Our Project", "Exact Proof for Faculty"),
        ("1", "Working Cloud App with Frontend, Backend & DB", "HTML5 UI, Python Flask REST API, and Amazon RDS MySQL.", "Open http://44.219.13.156:5000/ live in browser."),
        ("2", "Backend on EC2 / Compute (No pure serverless)", "Hosted on Amazon EC2 t2.micro (i-05c6a91b47a153e81) with systemd.", "Show EC2 Console: smart-campus-ec2 in Running state."),
        ("3", "Custom VPC with Subnets, Route Tables, IGW & SGs", "Deployed in vpc-08e22f2b09341874a with public/private subnets.", "Show VPC Console: subnets, IGW route, and Security Groups."),
        ("4", "Managed Database: Amazon RDS", "Amazon RDS MySQL (campus-complaints-db) on port 3306.", "Show RDS Console: campus-complaints-db in Available state."),
        ("5", "Amazon S3 for Genuine Requirement", "S3 Bucket (smart-campus-complaints-br2026x7) for evidence photos.", "Show S3 Console: complaints/ folder with uploaded images."),
        ("6", "IAM Least Privilege & No Hardcoded Keys", "EC2 uses IAM Instance Profile for S3 and SNS without keys.", "Show app.py initializing boto3 with NO hardcoded keys."),
        ("7", "Sensitive Config in SSM / Secure Mechanism", "DB credentials and secrets isolated in .env environment variables.", "Show .env.example and server environment variable isolation."),
        ("8", "CloudWatch Monitoring & at least 1 Alarm", "CloudWatch Alarm SmartCampus-HighCPU-Alarm on CPUUtilization > 80%.", "Show CloudWatch Console: Alarm in OK state."),
        ("9", "AWS Cloud Budget / Cost Alert", "Configured $1.00 Zero-Spend Budget with 80% threshold email alert.", "Show AWS Budgets dashboard with $1.00 active budget."),
        ("10", "Integrate at least 5 Cloud Services", "7 Services: EC2, RDS MySQL, S3, VPC, IAM, CloudWatch, and SNS.", "Show Architecture diagram and 7 console dashboards."),
        ("11", "At least 2 Additional Cloud Capabilities", "4 Capabilities: SNS push alerts, CloudWatch alarms, S3 Pre-Signed URLs, audit log.", "Demonstrate live SNS email upon status update."),
        ("12", "Serverless as Supporting Components Only", "Compliant. S3 and SNS are auxiliary; EC2 hosts core logic.", "Explain business logic execution on EC2 instance."),
        ("13", "Clear Functional Purpose for Every Service", "Every service is essential: Compute, DB, Storage, Security, Alerts.", "Refer to Master Service Table."),
        ("14", "Non-Trivial Project (Not Simple Static / CRUD)", "Full grievance state machine, tracking tokens, RBAC, and health API.", "Open /health endpoint showing live multi-cloud status."),
        ("15", "Demonstrates 5 Cloud Areas", "1. Compute, 2. Network, 3. DB, 4. Storage, 5. Security, 6. Monitoring.", "Exceeds requirement (6 of 5 cloud areas covered)."),
        ("16", "Free Tier Compliance & Cost Avoidance", "Single-AZ t2.micro, db.t3.micro, no expensive NAT Gateways.", "Show $0.00 / month cost breakdown table.")
    ]
    t2 = doc.add_table(rows=len(rubric), cols=4)
    w2 = [Inches(0.3), Inches(2.3), Inches(2.4), Inches(1.9)]
    for r_idx, row in enumerate(rubric):
        for c_idx, val in enumerate(row):
            cell = t2.cell(r_idx, c_idx)
            cell.width = w2[c_idx]
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.add_run(val)
    format_table(t2)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # 3. Top 10 Viva Q&A
    add_styled_heading(doc, "3. Top 10 Faculty Viva Trap Questions & Model Answers", level=1)
    
    qa = [
        ("Q1: Why is this project not considered a 'single EC2-hosted webpage'?",
         "A single EC2 webpage is a monolith where HTML files, SQLite databases, and user uploads are dumped onto the EC2 local hard drive. If that EC2 instance is terminated, 100% of the data is permanently lost. Our system implements a decoupled 3-tier enterprise architecture where the EC2 compute instance is completely stateless. Relational records live independently in Amazon RDS MySQL, and photos live independently in Amazon S3. Terminating our EC2 instance results in zero data loss."),
        ("Q2: How do you protect database and AWS credentials from leaking?",
         "We enforce two layers of security: First, for AWS services (S3 and SNS), we use an IAM Instance Profile attached to EC2. The AWS SDK (boto3) retrieves temporary rotating security tokens from the EC2 Instance Metadata Service (IMDSv2)—no AWS access keys exist anywhere in the code. Second, database credentials and session secrets are stored in .env environment variables that are excluded from Git version control via .gitignore."),
        ("Q3: Why did you use Amazon RDS instead of a local MySQL or SQLite database?",
         "A local database couples data to the compute instance, making horizontal scaling impossible and risking data loss upon instance failure. Amazon RDS MySQL provides a managed, enterprise-grade database service offering automated daily snapshots, OS maintenance, point-in-time recovery, independent storage scaling, and dedicated security group network isolation."),
        ("Q4: How does your S3 integration protect student photos from public access?",
         "The Amazon S3 bucket has 'Block all public access' enabled. The bucket is completely private. When an authenticated administrator needs to inspect evidence, our backend requests an AWS Signature Version 4 Pre-Signed URL via the AWS STS API. This URL grants temporary read access that automatically expires after 60 minutes, completely preventing unauthorized hotlinking or data leakage."),
        ("Q5: What is the functional purpose of Amazon SNS in your system?",
         "Amazon SNS decouples asynchronous incident notification from the web server. Instead of the web server waiting on slow SMTP mail servers, Flask publishes a lightweight pub/sub message to the SNS topic in milliseconds. SNS handles the message delivery, retries, and push notifications to student and administrator email endpoints simultaneously. Additionally, CloudWatch uses this same SNS topic to alert staff if server CPU exceeds 80%."),
        ("Q6: Explain your VPC network architecture and Security Group isolation.",
         "Our application resides within a custom Amazon VPC (10.0.0.0/16). The EC2 instance sits in a public subnet (10.0.6.0/24) with an attached Elastic IP and a route table pointing 0.0.0.0/0 to an Internet Gateway. Amazon RDS sits in a dedicated database subnet. For security, the EC2 security group allows ingress only on ports 80, 5000, and 22. Crucially, the RDS security group allows MySQL port 3306 exclusively from the EC2 Security Group ID, ensuring the database is completely unreachable from the public internet."),
        ("Q7: How did you ensure the project complied with the AWS Free Tier?",
         "We systematically avoided costly managed services. For instance, we avoided AWS NAT Gateways, which cost approximately $32.40/month, by utilizing an Internet Gateway and public subnet. We used single-AZ t2.micro for compute (750 free hours/month) and db.t3.micro for RDS (750 free hours/month). Finally, we configured an AWS Zero-Spend Budget with an 80% alert threshold ($0.80) to proactively guard against accidental charges."),
        ("Q8: How does your system handle server crashes or reboots?",
         "We configured a Linux systemd daemon (smart-campus.service) on the EC2 operating system. It has Restart=always and RestartSec=5 configured, and is enabled across system runlevels. If the Python process crashes, Linux restarts it within 5 seconds. If the entire EC2 instance reboots, systemd automatically boots the web server without requiring manual SSH intervention."),
        ("Q9: How does your database handle audit logging and grievance history?",
         "We architected an immutable audit trail using a dedicated complaint_history table linked via foreign key to the complaints table. Whenever an administrator changes a status (e.g. from Pending to Resolved), the application executes a transaction that updates the main status and appends a history record containing the previous status, new status, administrator username, timestamp, and administrative remarks."),
        ("Q10: How do you prove that your backend is actively communicating with cloud services?",
         "We built a dedicated health check endpoint at /health. When requested, the Flask backend validates live database connectivity to Amazon RDS MySQL, verifies the Amazon S3 bucket configuration, and checks the Amazon SNS topic ARN, returning a live JSON status report: {\"database\": \"Amazon RDS MySQL\", \"storage\": \"Amazon S3\", \"notifications\": \"Amazon SNS\", \"status\": \"ok\"}.")
    ]
    
    for q_text, a_text in qa:
        qp = doc.add_paragraph()
        qp.paragraph_format.space_before = Pt(8)
        qp.paragraph_format.space_after = Pt(2)
        q_run = qp.add_run(q_text)
        q_run.bold = True
        q_run.font.size = Pt(10)
        q_run.font.color.rgb = RGBColor(30, 58, 138)
        
        ap = doc.add_paragraph()
        ap.paragraph_format.space_before = Pt(0)
        ap.paragraph_format.space_after = Pt(6)
        a_run = ap.add_run(a_text)
        a_run.font.size = Pt(9.5)
        a_run.font.color.rgb = RGBColor(51, 65, 85)
        
    out = os.path.abspath("docs/VIVA_PREPARATION_GUIDE.docx")
    doc.save(out)
    print("Saved:", out)

if __name__ == "__main__":
    build_viva_doc()
