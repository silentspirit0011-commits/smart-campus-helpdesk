# 🎓 Smart Campus HelpDesk & Grievance Redressal System
### Production-Ready Decoupled 3-Tier Enterprise Cloud Architecture on AWS

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.x-black?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![AWS EC2](https://img.shields.io/badge/AWS-EC2-orange?logo=amazonec2&logoColor=white)](https://aws.amazon.com/ec2/)
[![AWS RDS](https://img.shields.io/badge/AWS-RDS%20MySQL-blue?logo=amazonrds&logoColor=white)](https://aws.amazon.com/rds/)
[![AWS S3](https://img.shields.io/badge/AWS-S3-red?logo=amazons3&logoColor=white)](https://aws.amazon.com/s3/)
[![AWS SNS](https://img.shields.io/badge/AWS-SNS-pink?logo=amazon-aws&logoColor=white)](https://aws.amazon.com/sns/)
[![AWS CloudWatch](https://img.shields.io/badge/AWS-CloudWatch-yellow?logo=amazoncloudwatch&logoColor=white)](https://aws.amazon.com/cloudwatch/)
[![Tests](https://img.shields.io/badge/Tests-11%2F11%20Passed-brightgreen?logo=pytest&logoColor=white)](tests/test_app.py)
[![Free Tier](https://img.shields.io/badge/Cost-%240.00%2Fmo%20(Free%20Tier)-success)](#-cost-optimization--free-tier-compliance)

---

## 📌 Executive Summary

Traditional campus complaint redressal mechanisms rely on physical paper forms, manual emails, or unmanaged spreadsheets. These methods suffer from lack of accountability, zero tracking visibility, lost attachments, and security vulnerabilities.

The **Smart Campus HelpDesk** is a production-ready, cloud-native web application built to streamline incident reporting, photographic evidence verification, and administrative resolution. The application is architected around a **stateless, decoupled 3-tier model** deployed across Amazon Web Services (AWS):

1. **Presentation Tier:** Responsive portal (HTML5, CSS3, Vanilla JavaScript) enabling students to file grievances, upload evidence photos, and track resolution timelines via unique tracking IDs (`CMP-XXXXXXXX`).
2. **Compute Tier:** Python 3 / Flask RESTful API hosted on **Amazon EC2 (`t2.micro`)** running Amazon Linux 2023, managed as a resilient background daemon via Linux `systemd`.
3. **Database Tier:** Managed relational records, foreign keys, and immutable audit logs persist in **Amazon RDS MySQL** (`campus_complaints`), isolated within a private database subnet.
4. **Storage Tier:** Photographic evidence attachments are offloaded to **Amazon S3** with time-limited cryptographic **AWS Signature Version 4 Pre-Signed URLs**.
5. **Notification & Monitoring Tier:** Real-time push email alerts powered by **Amazon SNS**, accompanied by infrastructure health telemetry and automated threshold alarms in **Amazon CloudWatch**.

---

## 🏗️ Cloud Architecture Diagram

```mermaid
graph TD
    User["Student / Public Browser"] -->|"HTTP: 80 / 5000"| EIP["Amazon Elastic IP<br/>(Permanent Static IPv4)"]
    Admin["Campus Administrator"] -->|"HTTP: 80 / 5000"| EIP
    
    EIP --> IGW["AWS Internet Gateway (IGW)"]
    IGW --> VPC["Custom Amazon VPC (10.0.0.0/16)"]
    
    subgraph VPC ["Custom Amazon VPC: vpc-08e22f2b09341874a"]
        subgraph PublicSubnet ["Public Web Subnet (10.0.6.0/24)"]
            SG_EC2["Security Group: smart-campus-ec2-sg<br/>Inbound: 80 (HTTP), 5000 (Flask), 22 (SSH)"]
            
            subgraph EC2_Box ["Amazon EC2 Instance: smart-campus-ec2 (t2.micro)"]
                Systemd["Linux systemd Service<br/>(smart-campus.service)"]
                Flask["Python 3 / Flask REST API<br/>(app.py)"]
                Systemd --> Flask
            end
            
            SG_EC2 --- EC2_Box
        end
        
        subgraph DBSubnet ["Isolated Database Subnet"]
            SG_RDS["Security Group: smart-campus-rds-sg<br/>Inbound: Port 3306 STRICTLY from smart-campus-ec2-sg"]
            RDS[("Amazon RDS MySQL Instance<br/>campus-complaints-db<br/>Database: campus_complaints")]
            SG_RDS --- RDS
        end
    end

    Flask -->|"PyMySQL / Prepared Statements (Port 3306)"| RDS
    Flask -->|"Direct Streaming & SigV4 Pre-Signed URLs"| S3[("Amazon S3 Bucket<br/>smart-campus-complaints-br2026x7<br/>Prefix: complaints/")]
    Flask -.->|"AWS SDK (boto3) via Instance Metadata (IMDSv2)"| IAM["AWS IAM Instance Role<br/>(Least-Privilege S3 & SNS Access)"]
    
    Flask -->|"Publish Complaint & Status Events"| SNS["Amazon SNS Topic<br/>smart-campus-notifications"]
    SNS -->|"Instant Email Alerts"| Inbox["Student & Admin Email Inboxes"]
    
    EC2_Box -.->|"Server Metrics (CPU, Memory, Network)"| CW["Amazon CloudWatch"]
    CW -->|"Trigger Alarm (>80% CPU Utilization)"| CWAlarm["CloudWatch Alarm:<br/>SmartCampus-HighCPU-Alarm"]
    CWAlarm -->|"Incident Notification"| SNS
```

---

## 🌟 Key Features & Capabilities

* **Decoupled 3-Tier Enterprise Architecture:** Compute (EC2), Database (RDS), and Storage (S3) operate independently. The EC2 instance is completely **stateless**—terminating the instance results in **zero data loss**.
* **Amazon RDS MySQL Relational Engine:** Enforces relational integrity, foreign keys, automated point-in-time snapshots, and parameterized SQL queries to prevent SQL injection.
* **Amazon S3 Object Storage with Pre-Signed URLs:** Evidence photos are stored in a private S3 bucket (public access blocked). Authorized admins inspect attachments via 60-minute expiring AWS Signature Version 4 URLs.
* **Amazon SNS Event-Driven Notifications:** Asynchronous push email notifications dispatched to students when complaint statuses transition to `In Progress` or `Resolved`, and to staff upon high-priority submissions.
* **Infrastructure Monitoring & Alarms:** Amazon CloudWatch monitors hypervisor-level telemetry and triggers `SmartCampus-HighCPU-Alarm` if CPU utilization breaches 80%.
* **Zero-Credential IAM Security:** Relies on an **IAM Instance Profile** using IMDSv2 temporary rotating tokens—no AWS access keys are hardcoded in the codebase.
* **Role-Based Access Control (RBAC):** Students access tickets via unique cryptographic tokens (`CMP-XXXXXXXX`). Admins authenticate using `pbkdf2:sha256` password hashing and `HttpOnly` / `SameSite=Lax` session cookies.
* **High-Availability Linux Daemon (`systemd`):** Configured with `Restart=always` and boot persistence, eliminating the need to manually execute terminal commands after instance reboots.
* **Infrastructure as Code (IaC):** Complete CloudFormation template ([docs/infrastructure.yaml](docs/infrastructure.yaml)) provisioning the VPC, subnets, security groups, S3 bucket, and EC2 instance programmatically.
* **Live Healthcheck Telemetry:** Dedicated endpoint (`/health`) verifying live connectivity across RDS MySQL, S3, and SNS.

---

## 📊 Faculty Rubric Compliance Matrix

| # | Faculty Condition / Requirement | How Met in Our Project | Status |
|---|----------------------------------|------------------------|:------:|
| **1** | Working cloud app with frontend, backend, and database | HTML5 UI + Flask REST API + Amazon RDS MySQL. Verified with 11/11 automated unit tests. | ✅ **MET** |
| **2** | Main application on EC2/containers (Serverless prohibited) | Hosted on **Amazon EC2 `t2.micro`** (`i-05c6a91b47a153e81`) running Amazon Linux 2023 with `systemd`. | ✅ **MET** |
| **3** | Custom VPC with subnets, route tables, IGW & Security Groups | Deployed in custom VPC (`vpc-08e22f2b09341874a`) with isolated subnets, IGW, and multi-tier Security Groups. | ✅ **MET** |
| **4** | Managed database such as Amazon RDS | **Amazon RDS MySQL** (`campus-complaints-db`) on port 3306 with automated backups. | ✅ **MET** |
| **5** | Amazon S3 for a genuine application requirement | **Amazon S3 Bucket** (`smart-campus-complaints-br2026x7`) storing grievance photos via Pre-Signed URLs. | ✅ **MET** |
| **6** | IAM roles/policies with least privilege; no hardcoded keys | EC2 uses IAM Instance Profile for S3 and SNS. **Zero hardcoded credentials** in code or Git. | ✅ **MET** |
| **7** | Sensitive config in SSM or secure mechanism | Database credentials, secret keys, and AWS configurations loaded via `.env` environment variables. | ✅ **MET** |
| **8** | CloudWatch monitoring & at least 1 meaningful alarm | CloudWatch Alarm `SmartCampus-HighCPU-Alarm` monitoring EC2 `CPUUtilization > 80%`. | ✅ **MET** |
| **9** | Cloud budget / cost alert within Free Tier | Configured **$1.00 Monthly Zero-Spend Budget** in AWS Budgets with email alerts. | ✅ **MET** |
| **10** | Integrate at least 5 Cloud Services | **7 Services Integrated:** EC2, RDS MySQL, S3, VPC, IAM, CloudWatch, and SNS. | ✅ **EXCEEDS** (7/5) |
| **11** | At least 2 additional cloud capabilities | 1. **Amazon SNS** email push alerts<br>2. **CloudWatch alarms**<br>3. **S3 Pre-Signed URLs**<br>4. **RDS Backup & Recovery**<br>5. **Infrastructure as Code (IaC)** | ✅ **EXCEEDS** (5/2) |
| **12** | Serverless as supporting components only | S3 and SNS act purely as auxiliary services; EC2 hosts the primary business logic. | ✅ **MET** |
| **13** | Clear functional purpose for every service | Every service solves a distinct, necessary architectural need (Compute, Storage, DB, Security, Alerts). | ✅ **MET** |
| **14** | Non-trivial project (Not simple static / basic CRUD) | Multi-tier grievance state machine (`Pending` $\rightarrow$ `In Progress` $\rightarrow$ `Resolved`), audit history, and RBAC. | ✅ **MET** |
| **15** | Demonstrates 5 Cloud Areas | 1. Compute, 2. Networking, 3. Database, 4. Storage, 5. Security/IAM, 6. Monitoring. | ✅ **EXCEEDS** (6/5) |
| **16** | Avoid expensive configurations (Free Tier compliance) | Single-AZ `t2.micro` EC2, `db.t3.micro` RDS, no costly NAT Gateways ($32/mo) or multi-AZ overhead. | ✅ **MET** |

---

## 🛠️ Technology Stack

| Layer | Technologies & Tools |
|---|---|
| **Frontend** | HTML5, CSS3, Vanilla JavaScript (ES6+), AJAX Fetch API |
| **Backend / API** | Python 3.9+, Flask, Werkzeug, PyMySQL, Boto3 (AWS SDK), python-dotenv |
| **Database** | Amazon RDS MySQL (Community Edition 8.0) / SQLite (Local Fallback) |
| **Compute** | Amazon EC2 (`t2.micro`), Amazon Linux 2023, Linux `systemd`, `iptables` |
| **Cloud Storage** | Amazon S3 (Standard Storage, Private Bucket, Pre-Signed URLs) |
| **Networking** | Amazon VPC, Public/Private Subnets, Internet Gateway, Elastic IP, Security Groups |
| **Security & IAM** | AWS IAM Instance Profile, IMDSv2, PBKDF2:SHA256 Password Hashing |
| **Monitoring & Alerts** | Amazon CloudWatch Alarms & Metrics, Amazon SNS (Pub/Sub Email) |
| **Cost Governance** | AWS Budgets ($1.00 Zero-Spend Budget) |
| **Infrastructure as Code** | AWS CloudFormation (YAML Template) |
| **Testing** | Pytest (11/11 automated unit & integration tests) |

---

## 📁 Repository Structure

```text
├── app.py                      # Core Flask RESTful backend & AWS SDK integrations
├── database.py                 # Dual-mode database abstraction (RDS MySQL + SQLite fallback)
├── requirements.txt            # Python production dependencies
├── .env.example                # Safe environment configuration template
├── .gitignore                  # Git exclusion rules for secrets, DB, and temporary files
├── CHANGELOG.md                # Development change history and version log
├── README.md                   # Comprehensive project documentation
│
├── docs/                       # Project documentation & examination materials
│   ├── PROJECT_REPORT.md       # Complete academic project submission report
│   ├── PROJECT_REPORT.docx     # Formatted Word Document version of report
│   ├── VIVA_PREPARATION_GUIDE.md # Viva Voce Q&A defense guide
│   ├── VIVA_PREPARATION_GUIDE.docx # Formatted Word Document for viva
│   └── infrastructure.yaml     # CloudFormation IaC template
│
├── templates/                  # Frontend HTML5 templates
│   ├── index.html              # Campus HelpDesk portal landing page
│   ├── complaint.html          # Student grievance filing interface
│   ├── track.html              # Public status tracking and history timeline
│   ├── admin.html              # Protected administrator management dashboard
│   └── login.html              # Secure administrator authentication page
│
├── static/                     # Frontend static assets
│   ├── css/
│   │   └── style.css           # Modern, responsive design system & UI tokens
│   └── js/
│       ├── complaint-api.js    # Asynchronous grievance submission & photo streaming
│       ├── track-api.js        # Dynamic timeline rendering & status lookup
│       └── admin-api.js        # Admin dashboard filters, analytics, & status updates
│
├── tests/                      # Automated test suite
│   └── test_app.py             # 11 unit & integration tests (Validation, Auth, S3, SNS, DB)
│
└── scripts/                    # Utility scripts
    ├── migrate_to_rds.py       # Data migration script (SQLite -> Amazon RDS MySQL)
    ├── create_word_doc.py      # Word document generator for Project Report
    └── create_viva_doc.py      # Word document generator for Viva Guide
```

---

## 🚀 Local Development & Quick Start

### 1. Clone Repository & Setup Virtual Environment
```bash
git clone https://github.com/silentspirit0011-commits/smart-campus-helpdesk.git
cd smart-campus-helpdesk

python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your local or cloud credentials
```

### 3. Run Automated Tests
```bash
pytest tests/test_app.py -v
```
All **11 unit and integration tests** will pass:
```text
tests/test_app.py::test_valid_submission PASSED                          [  9%]
tests/test_app.py::test_missing_and_invalid_fields PASSED                [ 18%]
tests/test_app.py::test_unique_tracking_ids PASSED                       [ 27%]
tests/test_app.py::test_tracking_valid_and_invalid_id PASSED             [ 36%]
tests/test_app.py::test_data_persistence_after_restart PASSED            [ 45%]
tests/test_app.py::test_admin_login_success_and_failure PASSED           [ 54%]
tests/test_app.py::test_unauthorized_admin_operations_rejected PASSED    [ 63%]
tests/test_app.py::test_successful_status_update_and_audit PASSED        [ 72%]
tests/test_app.py::test_dashboard_statistics PASSED                      [ 81%]
tests/test_app.py::test_database_error_handling PASSED                   [ 90%]
tests/test_app.py::test_sns_notification_triggers_on_status_update PASSED [100%]
============ 11 passed in 3.89s ============
```

### 4. Run the Development Server
```bash
python app.py
```
Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

---

## 🌐 Production AWS Cloud Deployment

On the Amazon EC2 instance:

```bash
# 1. Clone repository
git clone https://github.com/silentspirit0011-commits/smart-campus-helpdesk.git
cd smart-campus-helpdesk

# 2. Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configure production .env
cat << "EOF" > .env
FLASK_APP=app.py
SECRET_KEY=production-secure-random-key-here
DB_HOST=campus-complaints-db.c0rom2iier2a.us-east-1.rds.amazonaws.com
DB_USER=admin
DB_PASSWORD=your-db-password
DB_NAME=campus_complaints
DB_PORT=3306
S3_BUCKET_NAME=smart-campus-complaints-br2026x7
AWS_REGION=us-east-1
SNS_TOPIC_ARN=arn:aws:sns:us-east-1:983585032614:smart-campus-notifications
EOF

# 4. Setup systemd auto-start daemon
sudo bash -c 'cat << "EOF" > /etc/systemd/system/smart-campus.service
[Unit]
Description=Smart Campus HelpDesk Web Application
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/smart-campus-helpdesk
ExecStart=/home/ec2-user/smart-campus-helpdesk/venv/bin/python app.py
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF'

sudo systemctl daemon-reload
sudo systemctl enable smart-campus.service
sudo systemctl start smart-campus.service
```

---

## 📡 REST API Reference

| HTTP Method | Route Endpoint | Access Level | Description & Integration |
|:-----------:|:--------------:|:------------:|---------------------------|
| `GET` | `/` | Public | Campus portal landing page and navigation hub |
| `GET` | `/complaint` | Public | Student grievance submission form with photo upload |
| `GET` | `/track` | Public | Grievance status lookup and timeline search interface |
| `GET` | `/health` | Public | Live cloud service healthcheck (Amazon RDS + S3 + SNS) |
| `POST` | `/api/complaints` | Public | Submits complaint, streams photo to S3, returns tracking ID |
| `GET` | `/api/complaints/<id>` | Public | Fetches non-sensitive complaint details and status history |
| `GET` | `/api/complaints/<id>/image`| Admin | Generates expiring S3 Pre-Signed URL for evidence inspection |
| `POST` | `/admin/login` | Public | Authenticates administrator session using PBKDF2 hash |
| `GET` | `/admin` | Admin | Protected Administrator Management Dashboard |
| `GET` | `/api/complaints` | Admin | Lists all complaints from Amazon RDS MySQL for admin table |
| `GET` | `/api/complaints/statistics` | Admin | Calculates live metrics (Total, Pending, Progress, Resolved) |
| `POST` | `/api/complaints/<id>/status`| Admin | Updates status, records audit log, triggers Amazon SNS email |

---

## 💰 Cost Optimization & Free Tier Compliance

The entire infrastructure has been specifically sized to remain **100% within the AWS Free Tier**:

| Resource | Service Sizing | Monthly Usage | AWS Free Tier Allowance | Net Cost |
|----------|----------------|---------------|-------------------------|:--------:|
| **EC2 Instance** | `t2.micro` (1 vCPU, 1 GiB RAM) | 730 hours | 750 hours/month | **$0.00** |
| **Amazon RDS** | `db.t3.micro` Single-AZ (20 GB gp2) | 730 hours | 750 hours/month | **$0.00** |
| **Amazon S3** | Standard Storage Tier | < 1 GB | 5.0 GB/month | **$0.00** |
| **Network Egress** | Internet Gateway Data Transfer | < 5 GB | 100 GB/month free | **$0.00** |
| **CloudWatch** | 1 Custom Alarm + Basic Metrics | 1 Alarm | 10 Alarms free | **$0.00** |
| **Amazon SNS** | Push Email Notifications | < 1,000 emails | 100,000 free/month | **$0.00** |
| **TOTAL ESTIMATED COST** | | | | **$0.00 / month** |

---

## 👤 Author & Credits

* **GitHub:** [@silentspirit0011-commits](https://github.com/silentspirit0011-commits)
* **Project:** Cloud Computing Mini Project (Academic Year 2026–2027)
* **License:** [MIT License](LICENSE)
