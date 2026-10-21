"""
India Job Market Intelligence 2025
Phase 2: Comprehensive Dataset Generator
Description: Generates realistic job market data based on actual Naukri.com patterns
Note: This synthetic dataset mirrors real market trends for portfolio demonstration
"""

import os
import pandas as pd
import random
from datetime import datetime, timedelta
import numpy as np

# Seed for reproducibility
random.seed(42)
np.random.seed(42)

# ============================================================
# REAL MARKET DATA (Based on actual Naukri.com listings patterns)
# ============================================================

COMPANIES = {
    "top_tier": [
        "TCS", "Infosys", "Wipro", "HCL Technologies", "Tech Mahindra",
        "Cognizant", "Accenture", "IBM India", "Capgemini", "LTIMindtree"
    ],
    "product": [
        "Google India", "Microsoft India", "Amazon India", "Flipkart", "Paytm",
        "Swiggy", "Zomato", "PhonePe", "Razorpay", "CRED", "Meesho",
        "Zerodha", "Groww", "Ola", "Uber India", "Netflix India"
    ],
    "startups": [
        "Freshworks", "Zoho", "Dream11", "Unacademy", "BYJU'S",
        "Nykaa", "Urban Company", "PolicyBazaar", "CarDekho", "Lenskart",
        "Dunzo", "Rapido", "NoBroker", "UpGrad", "Simplilearn"
    ],
    "mnc": [
        "Deloitte", "EY", "KPMG", "PwC", "McKinsey", "BCG",
        "Goldman Sachs", "JP Morgan", "Morgan Stanley", "Barclays",
        "Deutsche Bank", "HSBC", "Citi", "American Express", "Visa"
    ],
    "mid_tier": [
        "Mphasis", "Hexaware", "Mindtree", "L&T Infotech", "Birlasoft",
        "Zensar", "Cyient", "Persistent Systems", "NIIT Technologies", "Sonata Software",
        "Happiest Minds", "Coforge", "KPIT Technologies", "Sasken Technologies", "Mastek"
    ]
}

CITIES = {
    "Bangalore": 0.30,
    "Mumbai": 0.18,
    "Delhi NCR": 0.15,
    "Hyderabad": 0.14,
    "Pune": 0.12,
    "Chennai": 0.07,
    "Remote": 0.04
}

JOB_ROLES = {
    "Data Analyst": {
        "titles": [
            "Data Analyst", "Junior Data Analyst", "Senior Data Analyst",
            "Business Data Analyst", "Product Data Analyst", "Marketing Data Analyst",
            "Financial Data Analyst", "Healthcare Data Analyst", "Data Analyst - Operations"
        ],
        "skills": [
            "SQL", "Python", "Excel", "Tableau", "Power BI", "Data Visualization",
            "Statistical Analysis", "R", "ETL", "Data Cleaning", "Pandas",
            "NumPy", "Google Analytics", "A/B Testing", "MySQL", "PostgreSQL",
            "Data Modeling", "Dashboard Development", "Reporting", "VBA"
        ],
        "weight": 0.35
    },
    "Data Scientist": {
        "titles": [
            "Data Scientist", "Junior Data Scientist", "Senior Data Scientist",
            "Machine Learning Engineer", "ML Engineer", "AI/ML Engineer",
            "Applied Data Scientist", "Research Scientist", "NLP Engineer"
        ],
        "skills": [
            "Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch",
            "SQL", "Statistics", "NLP", "Computer Vision", "Scikit-learn",
            "Keras", "AWS", "Azure ML", "Feature Engineering", "Model Deployment",
            "MLOps", "Spark", "Hadoop", "Neural Networks", "Time Series"
        ],
        "weight": 0.20
    },
    "Business Analyst": {
        "titles": [
            "Business Analyst", "Senior Business Analyst", "IT Business Analyst",
            "Technical Business Analyst", "Functional Analyst", "Systems Analyst",
            "Process Analyst", "Requirements Analyst", "Agile Business Analyst"
        ],
        "skills": [
            "SQL", "Excel", "JIRA", "Agile", "Scrum", "Requirements Gathering",
            "Business Process Modeling", "Stakeholder Management", "Documentation",
            "UAT", "Confluence", "Power BI", "Tableau", "User Stories", "Wireframing",
            "Data Analysis", "Project Management", "Communication", "Presentation"
        ],
        "weight": 0.25
    },
    "Python Developer": {
        "titles": [
            "Python Developer", "Senior Python Developer", "Python Backend Developer",
            "Django Developer", "Flask Developer", "Python Full Stack Developer",
            "Python Automation Engineer", "Python Software Engineer"
        ],
        "skills": [
            "Python", "Django", "Flask", "FastAPI", "REST API", "SQL",
            "PostgreSQL", "MongoDB", "Redis", "Docker", "AWS", "Git",
            "Linux", "OOPs", "Data Structures", "Algorithms", "Microservices",
            "Celery", "RabbitMQ", "Unit Testing", "CI/CD"
        ],
        "weight": 0.12
    },
    "SQL Developer": {
        "titles": [
            "SQL Developer", "Database Developer", "ETL Developer",
            "Data Engineer", "BI Developer", "Data Warehouse Developer",
            "PL/SQL Developer", "Database Administrator"
        ],
        "skills": [
            "SQL", "MySQL", "PostgreSQL", "Oracle", "SQL Server", "PL/SQL",
            "T-SQL", "ETL", "Data Warehousing", "SSIS", "Informatica",
            "Data Modeling", "Performance Tuning", "Stored Procedures",
            "Database Design", "NoSQL", "MongoDB", "Redshift", "Snowflake"
        ],
        "weight": 0.08
    }
}

EXPERIENCE_SALARY_MAP = {
    "0-1 Yrs": {"min": 2.5, "max": 5},
    "1-3 Yrs": {"min": 4, "max": 10},
    "3-5 Yrs": {"min": 8, "max": 18},
    "5-8 Yrs": {"min": 15, "max": 30},
    "8-12 Yrs": {"min": 25, "max": 50},
    "12+ Yrs": {"min": 40, "max": 80}
}

POSTED_LABELS = [
    "Today", "1 Day Ago", "2 Days Ago", "3 Days Ago", "4 Days Ago",
    "5 Days Ago", "1 Week Ago", "2 Weeks Ago", "3 Weeks Ago", "1 Month Ago"
]

POSTED_WEIGHTS = [0.15, 0.12, 0.12, 0.10, 0.10, 0.08, 0.10, 0.10, 0.08, 0.05]


def get_company():
    """Select a company with realistic distribution"""
    tier = random.choices(
        list(COMPANIES.keys()),
        weights=[0.30, 0.20, 0.15, 0.20, 0.15]
    )[0]
    return random.choice(COMPANIES[tier]), tier


def get_city():
    """Select city based on job market distribution"""
    cities = list(CITIES.keys())
    weights = list(CITIES.values())
    return random.choices(cities, weights=weights)[0]


def get_experience():
    """Get experience range with realistic distribution"""
    exp_ranges = list(EXPERIENCE_SALARY_MAP.keys())
    weights = [0.15, 0.30, 0.25, 0.15, 0.10, 0.05]
    return random.choices(exp_ranges, weights=weights)[0]


def get_salary(experience, company_tier):
    """Generate salary based on experience and company tier"""
    base = EXPERIENCE_SALARY_MAP[experience]
    
    # Adjust based on company tier
    multipliers = {
        "product": 1.4,
        "mnc": 1.2,
        "top_tier": 1.0,
        "startups": 1.1,
        "mid_tier": 0.9
    }
    
    mult = multipliers.get(company_tier, 1.0)
    min_sal = round(base["min"] * mult, 1)
    max_sal = round(base["max"] * mult, 1)
    
    # Some jobs don't disclose salary
    if random.random() < 0.25:
        return "Not Disclosed"
    
    return f"{min_sal}-{max_sal} Lacs PA"


def get_skills(role_data, count=None):
    """Select random skills for a role"""
    if count is None:
        count = random.randint(5, 10)
    skills = random.sample(role_data["skills"], min(count, len(role_data["skills"])))
    return ", ".join(skills)


def generate_job_listing(job_id):
    """Generate a single realistic job listing"""
    
    # Select role based on market distribution
    roles = list(JOB_ROLES.keys())
    weights = [JOB_ROLES[r]["weight"] for r in roles]
    role_category = random.choices(roles, weights=weights)[0]
    role_data = JOB_ROLES[role_category]
    
    # Get company and tier
    company, company_tier = get_company()
    
    # Get other attributes
    title = random.choice(role_data["titles"])
    city = get_city()
    experience = get_experience()
    salary = get_salary(experience, company_tier)
    skills = get_skills(role_data)
    posted = random.choices(POSTED_LABELS, weights=POSTED_WEIGHTS)[0]
    
    return {
        "job_id": f"JOB{job_id:06d}",
        "title": title,
        "company": company,
        "company_tier": company_tier,
        "location": city,
        "experience": experience,
        "salary": salary,
        "skills": skills,
        "role_category": role_category,
        "posted_date": posted,
        "data_source": "Naukri.com Pattern",
        "collected_date": datetime.now().strftime("%Y-%m-%d")
    }


def generate_dataset(n_jobs=1000):
    """Generate complete dataset"""
    print("=" * 60)
    print("🚀 GENERATING INDIA JOB MARKET DATASET")
    print("=" * 60)
    print(f"Target: {n_jobs} job listings")
    print(f"Based on: Real Naukri.com market patterns")
    print()
    
    jobs = []
    for i in range(1, n_jobs + 1):
        jobs.append(generate_job_listing(i))
        if i % 200 == 0:
            print(f"  ✓ Generated {i} jobs...")
    
    df = pd.DataFrame(jobs)
    
    print()
    print("=" * 60)
    print("✅ DATASET GENERATION COMPLETE")
    print("=" * 60)
    
    return df


def print_summary(df):
    """Print dataset summary statistics"""
    print("\n📊 DATASET SUMMARY")
    print("-" * 40)
    print(f"Total Jobs: {len(df)}")
    print(f"Unique Companies: {df['company'].nunique()}")
    print(f"Unique Titles: {df['title'].nunique()}")
    print()
    
    print("📍 Jobs by City:")
    city_dist = df['location'].value_counts()
    for city, count in city_dist.items():
        pct = count / len(df) * 100
        print(f"  {city}: {count} ({pct:.1f}%)")
    print()
    
    print("💼 Jobs by Role Category:")
    role_dist = df['role_category'].value_counts()
    for role, count in role_dist.items():
        pct = count / len(df) * 100
        print(f"  {role}: {count} ({pct:.1f}%)")
    print()
    
    print("📈 Jobs by Experience:")
    exp_dist = df['experience'].value_counts()
    for exp, count in exp_dist.items():
        pct = count / len(df) * 100
        print(f"  {exp}: {count} ({pct:.1f}%)")


if __name__ == "__main__":
    # Generate dataset
    df = generate_dataset(1200)
    
    # Save to CSV
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_file = os.path.join(root_dir, "data", "india_jobs_raw.csv")
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\n💾 Saved to: {output_file}")
    
    # Print summary
    print_summary(df)
    
    # Save column info
    print("\n📋 Columns:", list(df.columns))
