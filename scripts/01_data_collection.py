"""
India Job Market Intelligence 2025
Phase 2: Data Collection Script
Description: Scrapes job data from Naukri.com API for Data Analyst roles
"""

import requests
import json
import pandas as pd
import time
import os
from datetime import datetime

# Configuration
JOB_ROLES = [
    "data analyst",
    "data scientist", 
    "business analyst",
    "python developer",
    "sql developer"
]

CITIES = [
    "bangalore", "mumbai", "delhi ncr", 
    "hyderabad", "pune", "chennai", "remote"
]

def fetch_naukri_jobs(keyword, location="", page=1):
    """
    Fetch jobs from Naukri.com API
    """
    base_url = "https://www.naukri.com/jobapi/v3/search"
    
    params = {
        "noOfResults": 50,
        "urlType": "search_by_keyword",
        "searchType": "adv",
        "keyword": keyword,
        "pageNo": page,
        "sort": "r",  # relevance
        "seoKey": f"{keyword.replace(' ', '-')}-jobs"
    }
    
    if location:
        params["location"] = location
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "appid": "109",
        "systemid": "Naukri"
    }
    
    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"  Status {response.status_code} for {keyword}")
            return None
    except Exception as e:
        print(f"  Error: {e}")
        return None

def parse_job_data(job):
    """
    Extract relevant fields from job listing
    """
    try:
        # Extract placeholders (experience, salary, location)
        placeholders = job.get("placeholders", [])
        experience = ""
        salary = ""
        location = ""
        
        for p in placeholders:
            if p.get("type") == "experience":
                experience = p.get("label", "")
            elif p.get("type") == "salary":
                salary = p.get("label", "")
            elif p.get("type") == "location":
                location = p.get("label", "")
        
        return {
            "job_id": job.get("jobId", ""),
            "title": job.get("title", ""),
            "company": job.get("companyName", ""),
            "experience": experience,
            "salary": salary,
            "location": location,
            "skills": job.get("tagsAndSkills", ""),
            "posted_date": job.get("footerPlaceholderLabel", ""),
            "job_url": f"https://www.naukri.com{job.get('jdURL', '')}",
            "scraped_date": datetime.now().strftime("%Y-%m-%d")
        }
    except Exception as e:
        return None

def collect_all_jobs():
    """
    Main function to collect jobs for all roles
    """
    all_jobs = []
    
    print("=" * 60)
    print("🚀 INDIA JOB MARKET DATA COLLECTION")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    for role in JOB_ROLES:
        print(f"\n📊 Collecting: {role.upper()}")
        print("-" * 40)
        
        role_jobs = []
        
        # Collect multiple pages per role
        for page in range(1, 6):  # 5 pages = ~250 jobs per role
            print(f"  Page {page}...", end=" ")
            
            data = fetch_naukri_jobs(role, page=page)
            
            if data and "jobDetails" in data:
                jobs = data["jobDetails"]
                for job in jobs:
                    parsed = parse_job_data(job)
                    if parsed:
                        parsed["search_role"] = role
                        role_jobs.append(parsed)
                print(f"✓ Got {len(jobs)} jobs")
            else:
                print("✗ No data")
            
            time.sleep(1)  # Polite delay
        
        all_jobs.extend(role_jobs)
        print(f"  Total for {role}: {len(role_jobs)} jobs")
    
    print("\n" + "=" * 60)
    print(f"✅ TOTAL JOBS COLLECTED: {len(all_jobs)}")
    print("=" * 60)
    
    return all_jobs

def save_raw_data(jobs, filepath):
    """
    Save raw data to CSV
    """
    df = pd.DataFrame(jobs)
    df.to_csv(filepath, index=False, encoding='utf-8')
    print(f"💾 Saved raw data to: {filepath}")
    return df

if __name__ == "__main__":
    # Collect jobs
    jobs = collect_all_jobs()
    
    # Save raw data
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_file = os.path.join(root_dir, "data", "raw_jobs_data.csv")
    df = save_raw_data(jobs, raw_file)
    
    # Quick summary
    print("\n📈 QUICK SUMMARY:")
    print(f"  - Total Records: {len(df)}")
    print(f"  - Unique Companies: {df['company'].nunique()}")
    print(f"  - Job Roles: {df['search_role'].nunique()}")
    print(f"  - Columns: {list(df.columns)}")
