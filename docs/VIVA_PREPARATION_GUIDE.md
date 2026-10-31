# Smart Campus HelpDesk: Complete Viva Defense & Faculty Rubric Guide
## For Examination, Viva Voce & Technical Project Evaluation

---

## 📌 Document Purpose
This document is designed specifically for your **Project Viva & Demonstration**. It maps every single faculty requirement directly to what was built, explains how each component operates under the hood, and provides word-for-word technical answers to tough questions faculty evaluators ask.

---

## 1. Master Table: All Components (Frontend to Cloud Infrastructure)

| # | Component / AWS Service | Exact Resource Name / Identifier | Architecture Layer | What It Does (Plain English) | How It Works Technically Under the Hood (For Viva) |
|---|-------------------------|-----------------------------------|-------------------|------------------------------|---------------------------------------------------|
| **1** | **Web Frontend UI** | `templates/*.html`, `static/css`, `static/js` | **Presentation Tier** | User interface for filing grievances, tracking status, and admin operations. | Built with HTML5 semantic elements, responsive CSS flexbox/grid, and Vanilla JavaScript. Communicates asynchronously with the backend via RESTful `fetch()` AJAX APIs without full-page reloads. |
| **2** | **Flask REST API & Backend Engine** | `app.py`, `database.py` | **Application Tier** | Business logic, input validation, tracking code generation, RBAC auth, and cloud coordination. | Python 3 Flask microservice executing on WSGI. Validates input types and email regex, manages cryptographic session cookies (`HttpOnly`, `SameSite=Lax`), generates unique tracking tokens (`CMP-XXXXXXXX`), and interfaces with AWS SDK (`boto3`). |
| **3** | **Amazon EC2 (Virtual Compute)** | `smart-campus-ec2` (`i-05c6a91b47a153e81`) | **Compute Tier** | Runs the Python/Flask web application 24/7 on the cloud. | `t2.micro` virtual machine instance (1 vCPU, 1 GiB RAM) running Amazon Linux 2023. Governed by a Linux `systemd` daemon (`smart-campus.service`) ensuring automatic boot execution and crash recovery (`Restart=always`). |
| **4** | **AWS Elastic IP (EIP)** | `44.219.13.156` (Allocated IPv4) | **Networking Tier** | Permanent static public IP address for the web server. | Binds a fixed public IPv4 address to the EC2 network interface (ENI). Prevents URL disruption across instance stop/start cycles. |
| **5** | **Custom Amazon VPC & Subnets** | `vpc-08e22f2b09341874a` (`10.0.0.0/16`) | **Networking Tier** | Private virtual cloud network isolating application components. | Divides cloud infrastructure into a Public Subnet (`10.0.6.0/24`) connected to the Internet Gateway for web ingress, and a private Database Subnet group strictly isolated from direct internet access. |
| **6** | **Security Groups (Firewalls)** | `smart-campus-ec2-sg` & RDS SG | **Network Security** | Stateful firewalls controlling ingress and egress network packets. | `smart-campus-ec2-sg` allows Port 80 (HTTP), Port 5000 (Flask), and Port 22 (SSH). The RDS Security Group strictly allows MySQL Port 3306 **only from the EC2 Security Group ID**, blocking all direct public access. |
| **7** | **Amazon RDS MySQL** | `campus-complaints-db`<br>Endpoint: `campus-complaints-db...:3306` | **Database Tier** | Relational store for grievance records, lifecycle history, and admin credentials. | Managed MySQL Community Edition engine (`db.t3.micro`). Handles relational integrity, automated daily backups, and ACID transactions. Communicates with backend using parameterized SQL queries (`%s` in PyMySQL) to prevent SQL injection. |
| **8** | **Amazon S3 Object Storage** | Bucket: `smart-campus-complaints-br2026x7`<br>Prefix: `complaints/` | **Storage Tier** | Secure, durable cloud storage for student grievance evidence photos. | Object store offering 11 9's durability. The bucket is 100% private (public read blocked). File uploads are streamed via `s3.upload_fileobj()` with randomized UUIDs to prevent file overwrites. |
| **9** | **S3 Pre-Signed URLs** | AWS Signature Version 4 (SigV4) | **Storage Security** | Grants authorized admins temporary, expiring access to view photos. | When an admin clicks "View Evidence", Flask calls the AWS STS API to cryptographically sign a temporary URL valid for 3,600 seconds (1 hour). The S3 bucket remains strictly private. |
| **10** | **AWS IAM Instance Profile** | IAM Role attached to EC2 | **Security / Identity** | Grants EC2 permission to call S3 and SNS without passwords. | Leverages EC2 Instance Metadata Service (IMDSv2). Boto3 retrieves temporary, automatically rotating STS tokens. **Zero AWS Access Keys or Secrets are hardcoded in the codebase.** |
| **11** | **Amazon CloudWatch Alarm** | `SmartCampus-HighCPU-Alarm` | **Monitoring Tier** | Proactive infrastructure monitoring for server overload. | Hypervisor-level metric collector. If `CPUUtilization > 80%` for 2 consecutive 5-minute periods, the alarm state changes to `ALARM` and dispatches an incident message to SNS. |
| **12** | **Amazon SNS (Pub/Sub Alerts)** | Topic: `smart-campus-notifications` | **Messaging Tier** | Real-time push email notification system for students and staff. | Decoupled event notification broker. Publishes status events (e.g. `CMP-000107 is now RESOLVED`) and new complaint alerts, instantly pushing emails to verified subscriber endpoints. |
| **13** | **AWS Budgets Cost Alert** | `SmartCampus-FreeTier-Budget` | **Cost Governance** | Prevents unexpected cloud spending. | Monitors AWS billing telemetry. Configured as a Zero-Spend ($1.00) budget with an 80% threshold ($0.80) to alert the team if Free Tier allowances are breached. |

---

## 2. Direct Faculty Rubric Mapping & Defense Table

| # | Faculty Condition / Requirement | How We Met It in Our Project | Exact Proof to Show Faculty |
|---|----------------------------------|------------------------------|-----------------------------|
| **1** | **Working cloud app with frontend, backend, and database** | Complete full-stack system: HTML5/JS UI, Python Flask REST backend, and Amazon RDS MySQL. | Open `http://44.219.13.156:5000/`, submit a complaint, view tracking, and log into admin dashboard. |
| **2** | **Main application on EC2/containers (Serverless prohibited)** | Hosted on **Amazon EC2 `t2.micro`** (`i-05c6a91b47a153e81`) running Amazon Linux 2023 with `systemd`. | Show EC2 Management Console $\rightarrow$ instance `smart-campus-ec2` in `Running` state. |
| **3** | **Custom VPC with subnets, route tables, IGW & Security Groups** | Deployed in custom VPC (`vpc-08e22f2b09341874a`), public/private subnets, Internet Gateway, and tiered Security Groups. | Show VPC Console showing VPC ID, Subnet Route Tables routing to `igw-xxxx`, and Security Group rules. |
| **4** | **Managed database such as Amazon RDS** | **Amazon RDS MySQL** (`campus-complaints-db`). Tables: `complaints`, `complaint_history`, `admins`. | Show RDS Console showing `campus-complaints-db` in `Available` status on port 3306. |
| **5** | **Amazon S3 for a genuine application requirement** | **Amazon S3 Bucket** (`smart-campus-complaints-br2026x7`) storing grievance photographic evidence. | Show S3 Console $\rightarrow$ `complaints/` folder containing student uploaded image files with UUIDs. |
| **6** | **IAM roles/policies with least-privilege; no hardcoded keys** | EC2 uses IAM Instance Profile for S3 and SNS. Zero hardcoded AWS Access Keys in source code or Git. | Show `app.py` lines initializing `boto3.client('s3')` with NO credentials, and show IAM Role attached to EC2. |
| **7** | **Sensitive config in SSM or secure mechanism** | DB host, passwords, session secrets, and topic ARNs isolated in `.env` environment variables via `python-dotenv`. | Show `.env.example` in repo and explain environment variable isolation on the server. |
| **8** | **CloudWatch monitoring & at least 1 meaningful alarm** | CloudWatch Alarm `SmartCampus-HighCPU-Alarm` monitoring EC2 `CPUUtilization > 80%`. | Show CloudWatch Console $\rightarrow$ Alarms $\rightarrow$ `SmartCampus-HighCPU-Alarm` in **OK** state. |
| **9** | **Cloud budget / cost alert within Free Tier** | Configured **$1.00 Monthly Zero-Spend Budget** in AWS Budgets with email alerts. | Show AWS Budgets dashboard showing the active $1.00 budget and 80% threshold alert. |
| **10** | **Integrate at least 5 Cloud Services** | **7 Services Integrated:** EC2, RDS MySQL, S3, VPC, IAM, CloudWatch, and SNS. | Show Architecture diagram and console dashboards for all 7 services. |
| **11** | **At least 2 additional cloud capabilities** | Implemented **4 additional capabilities**: 1. Amazon SNS push notifications; 2. CloudWatch automated alarms; 3. S3 Pre-Signed URLs; 4. Relational status audit history. | Demonstrate live SNS email delivery upon status update, and explain S3 Pre-Signed URL expiration. |
| **12** | **Serverless as supporting components only** | Compliant. S3 and SNS serve purely as supporting storage/messaging services; EC2 hosts the core business logic. | Explain that business logic and REST APIs run on the EC2 compute instance. |
| **13** | **Clear functional purpose for every service** | Every service is essential: EC2 (API/Web), RDS (relational records), S3 (files), VPC (isolation), IAM (least-privilege), CloudWatch (health), SNS (notifications). | Refer to Master Service Table above. |
| **14** | **Non-trivial project (Not simple static / basic CRUD)** | Complete grievance lifecycle: Submission $\rightarrow$ Unique Token $\rightarrow$ Public Tracking $\rightarrow$ Admin PBKDF2 Auth $\rightarrow$ Department Analytics $\rightarrow$ Live Health API. | Open `/health` in browser showing real-time multi-cloud connectivity check. |
| **15** | **Demonstrates 5 Cloud Areas** | 1. Compute (EC2), 2. Networking (VPC/EIP/SG), 3. Database (RDS), 4. Storage (S3), 5. Security (IAM/Hashing), 6. Monitoring (CloudWatch/SNS). | Fulfills **6 out of 5** required cloud areas. |
| **16** | **Avoid expensive configurations (Free Tier compliance)** | Single-AZ `t2.micro` EC2, `db.t3.micro` RDS, no costly NAT Gateways ($32/mo) or multi-AZ instances. | Show Cost Breakdown table proving **$0.00 / month** Free Tier compliance. |

---

## 3. End-to-End Request Lifecycle (The "Life of a Grievance")

Walk your faculty through this step-by-step sequence during your demonstration:

```text
[Student Browser]
       │
       │  1. Submits grievance form with evidence photo via POST /api/complaints
       ▼
[Amazon EC2: Flask Backend (app.py)]
       │
       ├─► 2. Validates inputs & generates tracking ID: "CMP-000107"
       │
       ├─► 3. Streams photo to Amazon S3: "complaints/<uuid>_cable.jpg"
       │
       ├─► 4. Inserts relational record into Amazon RDS MySQL (complaints table)
       │
       └─► 5. Publishes event to Amazon SNS Topic (smart-campus-notifications)
               │
               ▼
       [Amazon SNS] ──► Dispatches email to Campus Maintenance Staff
       
[Public Tracking Page (/track)]
       │
       ▼  6. Student searches "CMP-000107" ──► Flask queries RDS ──► Displays status: "Pending"

[Admin Management Portal (/admin)]
       │
       ├─► 7. Admin logs in (Password verified against PBKDF2:SHA256 hash in RDS)
       │
       ├─► 8. Admin views photo (Backend requests S3 Pre-Signed URL valid for 60 mins)
       │
       └─► 9. Admin updates status to "Resolved" with remarks via POST /api/complaints/<id>/status
               │
               ├─► 10. Updates complaints table & logs audit entry in complaint_history table
               │
               └─► 11. Backend fires Amazon SNS Publish API
                       │
                       ▼
               [Amazon SNS] ──► Instant email delivered to Student: "[Smart Campus] Update: RESOLVED"
```

---

## 4. Top 10 Faculty Viva Trap Questions & Model Answers

### Q1: "Why is your project not considered a 'single EC2-hosted webpage'?"
> **Answer:** "A single EC2 webpage is a monolithic deployment where HTML files, SQLite databases, and user uploads are dumped onto the EC2 local hard drive. If that EC2 instance is terminated, 100% of the data is permanently lost. Our system implements a decoupled 3-tier enterprise architecture where the EC2 compute instance is **completely stateless**. Relational records live independently in Amazon RDS MySQL, and photos live independently in Amazon S3. Terminating our EC2 instance results in zero data loss."

### Q2: "How do you protect database and AWS credentials from leaking?"
> **Answer:** "We enforce two layers of security: First, for AWS services (S3 and SNS), we use an **IAM Instance Profile** attached to EC2. The AWS SDK (`boto3`) retrieves temporary rotating security tokens from the EC2 Instance Metadata Service (IMDSv2)—no AWS access keys exist anywhere in the code. Second, database credentials and session secrets are stored in `.env` environment variables that are excluded from Git version control via `.gitignore`."

### Q3: "Why did you use Amazon RDS instead of a local MySQL or SQLite database?"
> **Answer:** "A local database couples data to the compute instance, making horizontal scaling impossible and risking data loss upon instance failure. Amazon RDS MySQL provides a managed, enterprise-grade database service offering automated daily snapshots, OS maintenance, point-in-time recovery, independent storage scaling, and dedicated security group network isolation."

### Q4: "How does your S3 integration protect student photos from public access?"
> **Answer:** "The Amazon S3 bucket has **'Block all public access' enabled**. The bucket is completely private. When an authenticated administrator needs to inspect evidence, our backend requests an **AWS Signature Version 4 Pre-Signed URL** via the AWS STS API. This URL grants temporary read access that automatically expires after 60 minutes, completely preventing unauthorized hotlinking or data leakage."

### Q5: "What is the functional purpose of Amazon SNS in your system?"
> **Answer:** "Amazon SNS decouples asynchronous incident notification from the web server. Instead of the web server waiting on slow SMTP mail servers, Flask publishes a lightweight pub/sub message to the SNS topic in milliseconds. SNS handles the message delivery, retries, and push notifications to student and administrator email endpoints simultaneously. Additionally, CloudWatch uses this same SNS topic to alert staff if server CPU exceeds 80%."

### Q6: "Explain your VPC network architecture and Security Group isolation."
> **Answer:** "Our application resides within a custom Amazon VPC (`10.0.0.0/16`). The EC2 instance sits in a public subnet (`10.0.6.0/24`) with an attached Elastic IP and a route table pointing `0.0.0.0/0` to an Internet Gateway. Amazon RDS sits in a dedicated database subnet. For security, the EC2 security group allows ingress only on ports 80, 5000, and 22. Crucially, the **RDS security group allows MySQL port 3306 exclusively from the EC2 Security Group ID**, ensuring the database is completely unreachable from the public internet."

### Q7: "How did you ensure the project complied with the AWS Free Tier?"
> **Answer:** "We systematically avoided costly managed services. For instance, we avoided AWS NAT Gateways, which cost approximately $32.40/month, by utilizing an Internet Gateway and public subnet. We used single-AZ `t2.micro` for compute (750 free hours/month) and `db.t3.micro` for RDS (750 free hours/month). Finally, we configured an **AWS Zero-Spend Budget** with an 80% alert threshold ($0.80) to proactively guard against accidental charges."

### Q8: "How does your system handle server crashes or reboots?"
> **Answer:** "We configured a Linux `systemd` daemon (`smart-campus.service`) on the EC2 operating system. It has `Restart=always` and `RestartSec=5` configured, and is enabled across system runlevels. If the Python process crashes, Linux restarts it within 5 seconds. If the entire EC2 instance reboots, `systemd` automatically boots the web server without requiring manual SSH intervention."

### Q9: "How does your database handle audit logging and grievance history?"
> **Answer:** "We architected an immutable audit trail using a dedicated `complaint_history` table linked via foreign key to the `complaints` table. Whenever an administrator changes a status (e.g. from `Pending` to `Resolved`), the application executes a transaction that updates the main status and appends a history record containing the previous status, new status, administrator username, timestamp, and administrative remarks."

### Q10: "How do you prove that your backend is actively communicating with cloud services?"
> **Answer:** "We built a dedicated health check endpoint at `/health`. When requested, the Flask backend validates live database connectivity to Amazon RDS MySQL, verifies the Amazon S3 bucket configuration, and checks the Amazon SNS topic ARN, returning a live JSON status report: `{\"database\": \"Amazon RDS MySQL\", \"storage\": \"Amazon S3\", \"notifications\": \"Amazon SNS\", \"status\": \"ok\"}`."
