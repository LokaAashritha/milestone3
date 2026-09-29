import csv
import json
import os
import random
from datetime import datetime, timedelta

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
os.makedirs(DATA_DIR, exist_ok=True)

COMPANIES = [
    # --- Top Global & Indian MNCs ---
    {"name": "Google", "slug": "google", "company_type": "MNC", "is_newly_founded": False, "industry": "Internet & Cloud Technology", "headquarters": "Mountain View, CA (Bengaluru/Hyderabad)", "website": "https://careers.google.com", "founded_year": 1998, "employee_count_range": "10000+", "funding_stage": "Public / Post-IPO"},
    {"name": "Microsoft", "slug": "microsoft", "company_type": "MNC", "is_newly_founded": False, "industry": "Software & AI Solutions", "headquarters": "Redmond, WA (Hyderabad/Bengaluru/Noida)", "website": "https://careers.microsoft.com", "founded_year": 1975, "employee_count_range": "10000+", "funding_stage": "Public / Post-IPO"},
    {"name": "Amazon", "slug": "amazon", "company_type": "MNC", "is_newly_founded": False, "industry": "E-commerce & Cloud Computing (AWS)", "headquarters": "Seattle, WA (Bengaluru/Hyderabad/Chennai)", "website": "https://amazon.jobs", "founded_year": 1994, "employee_count_range": "10000+", "funding_stage": "Public / Post-IPO"},
    {"name": "Adobe", "slug": "adobe", "company_type": "MNC", "is_newly_founded": False, "industry": "Creative & Cloud Software", "headquarters": "San Jose, CA (Noida/Bengaluru)", "website": "https://adobe.com/careers", "founded_year": 1982, "employee_count_range": "10000+", "funding_stage": "Public / Post-IPO"},
    {"name": "Tata Consultancy Services (TCS)", "slug": "tcs", "company_type": "MNC", "is_newly_founded": False, "industry": "IT Services & Consulting", "headquarters": "Mumbai, India (Pan India)", "website": "https://tcs.com/careers", "founded_year": 1968, "employee_count_range": "10000+", "funding_stage": "Public / Post-IPO"},
    {"name": "Infosys", "slug": "infosys", "company_type": "MNC", "is_newly_founded": False, "industry": "Next-Gen Digital Services", "headquarters": "Bengaluru, India", "website": "https://infosys.com/careers", "founded_year": 1981, "employee_count_range": "10000+", "funding_stage": "Public / Post-IPO"},
    {"name": "Cisco", "slug": "cisco", "company_type": "MNC", "is_newly_founded": False, "industry": "Networking & Cybersecurity", "headquarters": "San Jose, CA (Bengaluru)", "website": "https://cisco.com/careers", "founded_year": 1984, "employee_count_range": "10000+", "funding_stage": "Public / Post-IPO"},
    {"name": "Oracle", "slug": "oracle", "company_type": "MNC", "is_newly_founded": False, "industry": "Database & Enterprise Cloud", "headquarters": "Austin, TX (Hyderabad/Bengaluru)", "website": "https://oracle.com/careers", "founded_year": 1977, "employee_count_range": "10000+", "funding_stage": "Public / Post-IPO"},
    {"name": "IBM", "slug": "ibm", "company_type": "MNC", "is_newly_founded": False, "industry": "Hybrid Cloud & Cognitive Enterprise", "headquarters": "Armonk, NY (Bengaluru/Kochi)", "website": "https://ibm.com/careers", "founded_year": 1911, "employee_count_range": "10000+", "funding_stage": "Public / Post-IPO"},
    {"name": "Salesforce", "slug": "salesforce", "company_type": "MNC", "is_newly_founded": False, "industry": "CRM & Enterprise SaaS", "headquarters": "San Francisco, CA (Hyderabad/Bengaluru)", "website": "https://salesforce.com/careers", "founded_year": 1999, "employee_count_range": "10000+", "funding_stage": "Public / Post-IPO"},

    # --- High-Growth Tech Startups & Unicorns ---
    {"name": "Razorpay", "slug": "razorpay", "company_type": "Startup", "is_newly_founded": False, "industry": "Fintech & Payments", "headquarters": "Bengaluru, Karnataka, India", "website": "https://razorpay.com/jobs", "founded_year": 2014, "employee_count_range": "1000-5000", "funding_stage": "Series F / Unicorn"},
    {"name": "Swiggy", "slug": "swiggy", "company_type": "Startup", "is_newly_founded": False, "industry": "Hyperlocal Delivery & Quick Commerce", "headquarters": "Bengaluru, Karnataka, India", "website": "https://careers.swiggy.com", "founded_year": 2014, "employee_count_range": "5000-10000", "funding_stage": "Public / Pre-IPO"},
    {"name": "CRED", "slug": "cred", "company_type": "Startup", "is_newly_founded": False, "industry": "Fintech & Rewards", "headquarters": "Bengaluru, Karnataka, India", "website": "https://cred.club/careers", "founded_year": 2018, "employee_count_range": "500-1000", "funding_stage": "Series E / Unicorn"},
    {"name": "Zepto", "slug": "zepto", "company_type": "Startup", "is_newly_founded": False, "industry": "Quick Commerce", "headquarters": "Mumbai / Bengaluru, India", "website": "https://zeptonow.com/careers", "founded_year": 2021, "employee_count_range": "1000-5000", "funding_stage": "Series G / Unicorn"},
    {"name": "Postman", "slug": "postman", "company_type": "Startup", "is_newly_founded": False, "industry": "API Development Platform", "headquarters": "San Francisco, CA & Bengaluru", "website": "https://postman.com/careers", "founded_year": 2014, "employee_count_range": "500-1000", "funding_stage": "Series D / Unicorn"},
    {"name": "Zerodha", "slug": "zerodha", "company_type": "Startup", "is_newly_founded": False, "industry": "Fintech & Stock Broking", "headquarters": "Bengaluru, Karnataka, India", "website": "https://zerodha.com/careers", "founded_year": 2010, "employee_count_range": "1000-5000", "funding_stage": "Bootstrapped / Profitable"},
    {"name": "Zomato", "slug": "zomato", "company_type": "Startup", "is_newly_founded": False, "industry": "Food Tech & Quick Commerce (Blinkit)", "headquarters": "Gurugram, Haryana, India", "website": "https://zomato.com/careers", "founded_year": 2008, "employee_count_range": "5000-10000", "funding_stage": "Public / Post-IPO"},
    {"name": "Groww", "slug": "groww", "company_type": "Startup", "is_newly_founded": False, "industry": "Investment Tech & Wealth Management", "headquarters": "Bengaluru, Karnataka, India", "website": "https://groww.in/careers", "founded_year": 2016, "employee_count_range": "1000-5000", "funding_stage": "Series E / Unicorn"},
    {"name": "PhonePe", "slug": "phonepe", "company_type": "Startup", "is_newly_founded": False, "industry": "Digital Payments & Financial Services", "headquarters": "Bengaluru, Karnataka, India", "website": "https://phonepe.com/careers", "founded_year": 2015, "employee_count_range": "5000-10000", "funding_stage": "Decacorn"},
    {"name": "Meesho", "slug": "meesho", "company_type": "Startup", "is_newly_founded": False, "industry": "E-Commerce & Social Selling", "headquarters": "Bengaluru, Karnataka, India", "website": "https://meesho.io/careers", "founded_year": 2015, "employee_count_range": "1000-5000", "funding_stage": "Series F / Unicorn"},
    {"name": "Urban Company", "slug": "urban-company", "company_type": "Startup", "is_newly_founded": False, "industry": "Home Services & Gig Economy", "headquarters": "Gurugram, Haryana, India", "website": "https://urbancompany.com/careers", "founded_year": 2014, "employee_count_range": "1000-5000", "funding_stage": "Series F / Unicorn"},

    # --- Newly Founded AI & Deep Tech Startups ---
    {"name": "NovaAI Labs", "slug": "novaai-labs", "company_type": "Newly Founded", "is_newly_founded": True, "industry": "Generative AI & Agentic Workflows", "headquarters": "Bengaluru (Remote-First)", "website": "https://novaailabs.dev", "founded_year": 2024, "employee_count_range": "1-20", "funding_stage": "Seed ($2M)"},
    {"name": "SynthLogic Systems", "slug": "synthlogic", "company_type": "Newly Founded", "is_newly_founded": True, "industry": "AI Career Intelligence & HR Tech", "headquarters": "Pune / Remote", "website": "https://synthlogicsys.io", "founded_year": 2024, "employee_count_range": "1-15", "funding_stage": "Pre-Seed ($500K)"},
    {"name": "NeuralScale Dynamics", "slug": "neuralscale", "company_type": "Newly Founded", "is_newly_founded": True, "industry": "Deep Learning & Model Optimization", "headquarters": "Hyderabad, Telangana", "website": "https://neuralscale.ai", "founded_year": 2023, "employee_count_range": "1-25", "funding_stage": "Seed ($3M)"},
    {"name": "PromptCraft AI", "slug": "promptcraft-ai", "company_type": "Newly Founded", "is_newly_founded": True, "industry": "AI Developer Tooling & LLM Eval", "headquarters": "Delhi NCR / Remote", "website": "https://promptcraft.studio", "founded_year": 2024, "employee_count_range": "1-10", "funding_stage": "Bootstrapped"},
    {"name": "DataVortex Technologies", "slug": "datavortex", "company_type": "Newly Founded", "is_newly_founded": True, "industry": "Real-time Vector Search & RAG", "headquarters": "Bengaluru, India", "website": "https://datavortex.tech", "founded_year": 2023, "employee_count_range": "1-15", "funding_stage": "Seed ($1.5M)"},
    {"name": "CogniGen Systems", "slug": "cognigen", "company_type": "Newly Founded", "is_newly_founded": True, "industry": "Autonomous Agents for Healthcare", "headquarters": "Chennai / Remote", "website": "https://cognigen.ai", "founded_year": 2024, "employee_count_range": "1-12", "funding_stage": "Pre-Seed ($750K)"},
    {"name": "OmniAgentic AI", "slug": "omniagentic", "company_type": "Newly Founded", "is_newly_founded": True, "industry": "Multi-Agent Code Synthesis", "headquarters": "Bengaluru / Remote", "website": "https://omniagentic.dev", "founded_year": 2024, "employee_count_range": "1-10", "funding_stage": "Seed ($2.5M)"},
    {"name": "ByteForge Tech", "slug": "byteforge", "company_type": "Newly Founded", "is_newly_founded": True, "industry": "Edge AI & Embedded Computing", "headquarters": "Pune, Maharashtra", "website": "https://byteforge.io", "founded_year": 2023, "employee_count_range": "1-20", "funding_stage": "Seed ($1.2M)"}
]

JOB_TEMPLATES = [
    {
        "title": "Backend Software Engineer (Python / FastAPI)",
        "role_category": "Backend",
        "skills": ["Python", "FastAPI", "PostgreSQL", "Redis", "Docker", "REST APIs", "Microservices"],
        "job_type": "Full-time",
        "salary_min": 1400000, "salary_max": 2400000,
        "experience_level": "Mid-level", "exp_min": 2, "exp_max": 5, "fresher": False,
        "description": "Design and build high-throughput RESTful services and distributed data pipelines.",
        "responsibilities": "Develop modular backend microservices in FastAPI; optimize database queries in PostgreSQL; configure Redis caching.",
        "requirements": "Strong background in Python 3.10+, SQLAlchemy, async programming, and Docker containerization."
    },
    {
        "title": "Junior Python Developer (Fresher Friendly)",
        "role_category": "Backend",
        "skills": ["Python", "FastAPI", "SQL", "Git", "REST APIs", "Data Structures"],
        "job_type": "Full-time",
        "salary_min": 600000, "salary_max": 950000,
        "experience_level": "Fresher", "exp_min": 0, "exp_max": 1, "fresher": True,
        "description": "Kickstart your software engineering journey with mentorship from experienced architects.",
        "responsibilities": "Write clean Python code for CRUD operations; participate in code reviews and unit test writing in Pytest.",
        "requirements": "B.Tech/B.E/BCA/MCA graduate with strong fundamentals in Python, OOP concepts, and SQL basics."
    },
    {
        "title": "Frontend Engineer (React.js, TypeScript & Tailwind)",
        "role_category": "Frontend",
        "skills": ["React", "TypeScript", "Tailwind CSS", "Redux", "Framer Motion", "REST APIs", "Next.js"],
        "job_type": "Full-time",
        "salary_min": 1200000, "salary_max": 2200000,
        "experience_level": "Mid-level", "exp_min": 2, "exp_max": 4, "fresher": False,
        "description": "Craft responsive swipe interfaces, analytics dashboards, and interactive user journeys.",
        "responsibilities": "Build modular UI components in React with Tailwind CSS; integrate REST APIs with graceful error handling.",
        "requirements": "2+ years experience with modern React, TypeScript, state management (Redux/Context), and CSS animations."
    },
    {
        "title": "Frontend Developer Intern (React & UI Design)",
        "role_category": "Frontend",
        "skills": ["React", "JavaScript", "HTML5", "CSS3", "Tailwind CSS", "Git"],
        "job_type": "Internship",
        "salary_min": 25000, "salary_max": 45000,
        "experience_level": "Fresher", "exp_min": 0, "exp_max": 1, "fresher": True,
        "description": "Hands-on frontend internship building swipe-based job discovery cards and mobile-first layouts.",
        "responsibilities": "Convert Figma designs to clean React components; implement responsive layouts and micro-interactions.",
        "requirements": "Demonstrated personal projects in React.js and strong knowledge of modern CSS/Tailwind."
    },
    {
        "title": "Full Stack Engineer (FastAPI + React)",
        "role_category": "Full Stack",
        "skills": ["Python", "FastAPI", "React", "TypeScript", "PostgreSQL", "Docker", "Tailwind CSS"],
        "job_type": "Full-time",
        "salary_min": 1600000, "salary_max": 2800000,
        "experience_level": "Mid-level", "exp_min": 3, "exp_max": 6, "fresher": False,
        "description": "Lead end-to-end feature delivery across frontend client apps and scalable backend services.",
        "responsibilities": "Architect database schemas, implement business APIs, and craft pixel-perfect user dashboards.",
        "requirements": "Full-stack proficiency with Python/FastAPI backend and React/Next.js frontend."
    },
    {
        "title": "AI / Machine Learning Engineer (NLP & Vector Search)",
        "role_category": "AI/ML",
        "skills": ["Python", "PyTorch", "Hugging Face", "spaCy", "sentence-transformers", "Vector DB", "ChromaDB", "scikit-learn"],
        "job_type": "Full-time",
        "salary_min": 1800000, "salary_max": 3200000,
        "experience_level": "Mid-level", "exp_min": 2, "exp_max": 5, "fresher": False,
        "description": "Develop semantic matching engines, ATS scoring models, and candidate recommendation algorithms.",
        "responsibilities": "Train embedding models for resume-to-job similarity; optimize cosine distance calculations; build ML inference APIs.",
        "requirements": "Proven experience in NLP, embeddings, vector similarity search, and deep learning frameworks."
    },
    {
        "title": "AI Research & NLP Intern",
        "role_category": "AI/ML",
        "skills": ["Python", "Pandas", "NumPy", "scikit-learn", "spaCy", "NLP", "PyTorch"],
        "job_type": "Internship",
        "salary_min": 35000, "salary_max": 60000,
        "experience_level": "Fresher", "exp_min": 0, "exp_max": 1, "fresher": True,
        "description": "Join our AI research team to perform exploratory data analysis on resume datasets and fine-tune NLP tokenizers.",
        "responsibilities": "Perform EDA and data cleaning on unstructured text; evaluate heuristic vs transformer matching scores.",
        "requirements": "Strong Python coding ability and academic foundation in statistical machine learning and NLP."
    },
    {
        "title": "Generative AI & LLM Systems Engineer",
        "role_category": "AI/ML",
        "skills": ["Python", "OpenAI API", "LangChain", "LlamaIndex", "RAG", "Prompt Engineering", "FastAPI"],
        "job_type": "Full-time",
        "salary_min": 2400000, "salary_max": 4200000,
        "experience_level": "Senior", "exp_min": 4, "exp_max": 8, "fresher": False,
        "description": "Architect autonomous AI agents, structured LLM extraction pipelines, and RAG document search systems.",
        "responsibilities": "Build agentic workflows with LangChain; implement prompt guardrails and evaluation metrics; optimize token latency.",
        "requirements": "4+ years engineering experience with 2+ years deploying production RAG / LLM systems."
    },
    {
        "title": "Data Analyst (Job Market & Hiring Intelligence)",
        "role_category": "Data Analytics",
        "skills": ["SQL", "Python", "Pandas", "Tableau", "PowerBI", "Data Modeling", "Excel"],
        "job_type": "Full-time",
        "salary_min": 850000, "salary_max": 1500000,
        "experience_level": "Entry-level", "exp_min": 1, "exp_max": 3, "fresher": True,
        "description": "Analyze salary benchmarks, hiring velocity, and user swipe engagement patterns to generate market insights.",
        "responsibilities": "Write complex SQL queries for analytics; build executive Tableau dashboards; calculate candidate conversion funnels.",
        "requirements": "Proficient in SQL and statistical data analysis in Python (Pandas/Seaborn)."
    },
    {
        "title": "DevOps & Cloud Infrastructure Engineer",
        "role_category": "DevOps",
        "skills": ["Docker", "Kubernetes", "AWS", "GitHub Actions", "Terraform", "Linux", "PostgreSQL", "Redis"],
        "job_type": "Full-time",
        "salary_min": 1500000, "salary_max": 2600000,
        "experience_level": "Mid-level", "exp_min": 2, "exp_max": 5, "fresher": False,
        "description": "Maintain containerized multi-service architectures and automate continuous integration and deployment pipelines.",
        "responsibilities": "Configure Docker Compose and Kubernetes pods; maintain CI workflows; manage AWS cloud resources.",
        "requirements": "Solid experience in Docker containerization, Linux systems administration, and GitHub Actions CI."
    },
    {
        "title": "Software Development Engineer in Test (SDET / QA)",
        "role_category": "QA/Testing",
        "skills": ["Python", "Pytest", "Postman", "REST APIs", "Selenium", "Jest", "CI/CD"],
        "job_type": "Full-time",
        "salary_min": 800000, "salary_max": 1400000,
        "experience_level": "Entry-level", "exp_min": 1, "exp_max": 3, "fresher": True,
        "description": "Build automated test suites for REST APIs, validate RBAC security policies, and maintain regression test beds.",
        "responsibilities": "Develop automated integration test cases using Pytest; maintain Postman collections; perform load and security tests.",
        "requirements": "Strong Python test automation skills and deep understanding of HTTP status codes and API specifications."
    },
    {
        "title": "Product Designer (UI/UX & Mobile Interactions)",
        "role_category": "Design",
        "skills": ["Figma", "UI/UX Design", "Wireframing", "Prototyping", "Design Systems", "User Research"],
        "job_type": "Full-time",
        "salary_min": 1100000, "salary_max": 1900000,
        "experience_level": "Mid-level", "exp_min": 2, "exp_max": 4, "fresher": False,
        "description": "Design high-converting swipe interfaces, seamless recruiter portals, and accessible design system components.",
        "responsibilities": "Create user flows, wireframes, and interactive prototypes in Figma; conduct usability tests with job seekers.",
        "requirements": "Strong design portfolio with expertise in auto-layout, mobile micro-interactions, and design systems."
    }
]

LOCATIONS = [
    "Bengaluru, Karnataka, India",
    "Hyderabad, Telangana, India",
    "Pune, Maharashtra, India",
    "Mumbai, Maharashtra, India",
    "Delhi NCR / Gurugram, India",
    "Noida, Uttar Pradesh, India",
    "Chennai, Tamil Nadu, India",
    "Remote, India",
    "Remote (Global)"
]

WORKPLACE_TYPES = ["On-site", "Hybrid", "Remote"]


def generate_datasets():
    print(f"Generating comprehensive dataset files inside: {DATA_DIR}")

    # 1. Save Companies Dataset CSV
    companies_csv_path = os.path.join(DATA_DIR, "companies_dataset.csv")
    with open(companies_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "company_id", "name", "slug", "company_type", "is_newly_founded", "industry", 
            "headquarters", "funding_stage", "website", "founded_year", "employee_count_range"
        ])
        writer.writeheader()
        for i, c in enumerate(COMPANIES, start=1):
            row = {
                "company_id": i,
                "name": c["name"],
                "slug": c["slug"],
                "company_type": c["company_type"],
                "is_newly_founded": c["is_newly_founded"],
                "industry": c["industry"],
                "headquarters": c["headquarters"],
                "funding_stage": c["funding_stage"],
                "website": c["website"],
                "founded_year": c["founded_year"],
                "employee_count_range": c["employee_count_range"]
            }
            writer.writerow(row)

    print(f" Created {companies_csv_path} ({len(COMPANIES)} companies)")

    # 2. Generate 300+ Realistic Jobs Dataset CSV & JSON
    jobs_rows = []
    job_id_counter = 1
    now = datetime.utcnow()

    for comp_id, company in enumerate(COMPANIES, start=1):
        num_postings = random.randint(9, 13)
        selected_templates = random.sample(JOB_TEMPLATES * 2, num_postings)

        for tmpl in selected_templates:
            loc = random.choice(LOCATIONS)
            workplace = random.choice(WORKPLACE_TYPES)
            if "Remote" in loc:
                workplace = "Remote"

            if company["company_type"] == "MNC":
                competition = random.choice(["High", "High", "Medium"])
                applicants = random.randint(50, 220)
                sal_multiplier = random.uniform(1.0, 1.25)
            elif company["company_type"] == "Startup":
                competition = random.choice(["Medium", "Low", "Medium"])
                applicants = random.randint(15, 80)
                sal_multiplier = random.uniform(0.95, 1.35)
            else:  # Newly Founded
                competition = "Low"
                applicants = random.randint(3, 20)
                sal_multiplier = random.uniform(0.85, 1.15)

            sal_min = int(tmpl["salary_min"] * sal_multiplier)
            sal_max = int(tmpl["salary_max"] * sal_multiplier)
            sal_period = "Per Month" if tmpl["job_type"] == "Internship" else "Per Annum"

            days_ago = random.randint(0, 18)
            posted_date = (now - timedelta(days=days_ago, hours=random.randint(1, 23))).strftime("%Y-%m-%d %H:%M:%S")

            freshness_label = "Just Posted" if days_ago <= 1 else ("Recently Posted" if days_ago <= 3 else "Active")

            job_record = {
                "job_id": job_id_counter,
                "company_id": comp_id,
                "company_name": company["name"],
                "company_type": company["company_type"],
                "is_newly_founded": company["is_newly_founded"],
                "company_industry": company["industry"],
                "job_title": tmpl["title"],
                "role_category": tmpl["role_category"],
                "job_description": tmpl["description"],
                "responsibilities": tmpl["responsibilities"],
                "requirements": tmpl["requirements"],
                "skills_required": json.dumps(tmpl["skills"]),
                "required_skills": json.dumps(tmpl["skills"]),
                "keywords": json.dumps(
                    {
                        "Backend": ["RESTful APIs", "Microservices", "Docker", "CI/CD", "PostgreSQL", "Database Optimization", "Scalability"],
                        "Frontend": ["Responsive Design", "State Management", "Component Architecture", "Accessibility", "Tailwind CSS", "TypeScript"],
                        "Full Stack": ["REST APIs", "Full Stack Architecture", "Docker", "SQL", "Frontend Integration", "System Design"],
                        "AI/ML": ["Machine Learning", "NLP", "Vector Search", "Embeddings", "LLMs", "Deep Learning", "Transformers"],
                        "Data Analytics": ["Data Analysis", "SQL Queries", "ETL", "Dashboarding", "Statistical Analysis", "Business Intelligence"],
                        "QA/Testing": ["Test Automation", "Pytest", "Integration Testing", "Regression Testing", "API Testing", "CI/CD"],
                        "Design": ["User Research", "Wireframing", "Interactive Prototyping", "Design Systems", "Figma", "Usability Testing"],
                        "Mobile": ["Mobile Architecture", "iOS", "Android", "Cross-Platform", "App Performance", "Offline Storage"],
                        "DevOps": ["Kubernetes", "Docker", "CI/CD Pipelines", "Terraform", "Infrastructure as Code", "Monitoring"]
                    }.get(tmpl["role_category"], ["Agile", "Git", "Problem Solving", "Collaboration", "Software Engineering"])
                ),
                "job_type": tmpl["job_type"],
                "workplace_type": workplace,
                "location": loc,
                "salary_min": sal_min,
                "salary_max": sal_max,
                "salary_currency": "INR",
                "salary_period": sal_period,
                "experience_level": tmpl["experience_level"],
                "experience_years_min": tmpl["exp_min"],
                "experience_years_max": tmpl["exp_max"],
                "competition_level": competition,
                "applicant_count": applicants,
                "is_fresher_friendly": tmpl["fresher"],
                "is_early_applicant": applicants < 15,
                "freshness_label": freshness_label,
                "is_active": True,
                "posted_at": posted_date
            }
            jobs_rows.append(job_record)
            job_id_counter += 1

    # Write jobs CSV
    jobs_csv_path = os.path.join(DATA_DIR, "jobs_dataset.csv")
    with open(jobs_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(jobs_rows[0].keys()))
        writer.writeheader()
        for row in jobs_rows:
            writer.writerow(row)

    print(f" Created {jobs_csv_path} ({len(jobs_rows)} rich job postings)")

    # Write jobs JSON
    jobs_json_path = os.path.join(DATA_DIR, "jobs_dataset.json")
    with open(jobs_json_path, "w", encoding="utf-8") as f:
        json.dump(jobs_rows, f, indent=2, ensure_ascii=False)

    print(f" Created {jobs_json_path}")
    print(f"Successfully generated all datasets in '{DATA_DIR}'!")


if __name__ == "__main__":
    generate_datasets()
