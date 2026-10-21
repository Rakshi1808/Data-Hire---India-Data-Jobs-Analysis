"""
India Job Market Intelligence 2025
Phase 4: SQL Database & Analysis
Description: Creates SQLite database and runs analytical queries
"""

import sqlite3
import pandas as pd
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(ROOT_DIR, "output")

# Database and file paths
DB_PATH = os.path.join(ROOT_DIR, "data", "india_jobs.db")
DATA_PATH = os.path.join(ROOT_DIR, "data", "india_jobs_cleaned.csv")
QUERIES_OUTPUT = os.path.join(ROOT_DIR, "sql", "analysis_results.txt")

def create_database():
    """Create SQLite database from cleaned CSV"""
    print("=" * 60)
    print("🗄️  CREATING SQL DATABASE")
    print("=" * 60)
    
    # Load cleaned data
    df = pd.read_csv(DATA_PATH)
    
    # Remove the skills_list column (contains Python list, not SQL friendly)
    if 'skills_list' in df.columns:
        df = df.drop('skills_list', axis=1)
    
    # Connect to SQLite
    conn = sqlite3.connect(DB_PATH)
    
    # Create main jobs table
    df.to_sql('jobs', conn, if_exists='replace', index=False)
    print(f"✓ Created 'jobs' table with {len(df)} records")
    
    # Create skills lookup table (normalized)
    skills_data = []
    df_original = pd.read_csv(DATA_PATH)
    for idx, row in df_original.iterrows():
        job_id = row['job_id']
        skills = str(row['skills']).split(', ')
        for skill in skills:
            skills_data.append({'job_id': job_id, 'skill': skill.strip()})
    
    skills_df = pd.DataFrame(skills_data)
    skills_df.to_sql('job_skills', conn, if_exists='replace', index=False)
    print(f"✓ Created 'job_skills' table with {len(skills_df)} records")
    
    conn.close()
    print(f"\n💾 Database saved: {DB_PATH}")
    return True


def run_analysis_queries():
    """Run comprehensive analysis queries"""
    print("\n" + "=" * 60)
    print("📊 RUNNING ANALYSIS QUERIES")
    print("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    results = []
    
    queries = {
        # Query 1: Top 10 Skills in Demand
        "TOP 10 SKILLS IN DEMAND": """
            SELECT 
                skill,
                COUNT(*) as job_count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(DISTINCT job_id) FROM job_skills), 1) as percentage
            FROM job_skills
            GROUP BY skill
            ORDER BY job_count DESC
            LIMIT 10
        """,
        
        # Query 2: Jobs by City
        "JOBS DISTRIBUTION BY CITY": """
            SELECT 
                location,
                COUNT(*) as job_count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM jobs), 1) as percentage
            FROM jobs
            GROUP BY location
            ORDER BY job_count DESC
        """,
        
        # Query 3: Jobs by Role Category
        "JOBS BY ROLE CATEGORY": """
            SELECT 
                role_category,
                COUNT(*) as job_count,
                ROUND(AVG(salary_avg), 1) as avg_salary_lpa
            FROM jobs
            WHERE salary_avg IS NOT NULL
            GROUP BY role_category
            ORDER BY job_count DESC
        """,
        
        # Query 4: Salary Analysis by Experience
        "SALARY BY EXPERIENCE LEVEL": """
            SELECT 
                experience_level,
                COUNT(*) as job_count,
                ROUND(AVG(salary_avg), 1) as avg_salary,
                ROUND(MIN(salary_avg), 1) as min_salary,
                ROUND(MAX(salary_avg), 1) as max_salary
            FROM jobs
            WHERE salary_avg IS NOT NULL
            GROUP BY experience_level
            ORDER BY avg_salary DESC
        """,
        
        # Query 5: Top Hiring Companies
        "TOP 15 HIRING COMPANIES": """
            SELECT 
                company,
                company_tier,
                COUNT(*) as job_count,
                ROUND(AVG(salary_avg), 1) as avg_salary
            FROM jobs
            GROUP BY company
            ORDER BY job_count DESC
            LIMIT 15
        """,
        
        # Query 6: Salary Brackets Distribution
        "SALARY BRACKETS DISTRIBUTION": """
            SELECT 
                salary_bracket,
                COUNT(*) as job_count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM jobs), 1) as percentage
            FROM jobs
            GROUP BY salary_bracket
            ORDER BY 
                CASE salary_bracket
                    WHEN '< 5 LPA' THEN 1
                    WHEN '5-10 LPA' THEN 2
                    WHEN '10-20 LPA' THEN 3
                    WHEN '20-35 LPA' THEN 4
                    WHEN '35+ LPA' THEN 5
                    ELSE 6
                END
        """,
        
        # Query 7: Skills by Role
        "TOP SKILLS FOR DATA ANALYST": """
            SELECT 
                js.skill,
                COUNT(*) as count
            FROM job_skills js
            JOIN jobs j ON js.job_id = j.job_id
            WHERE j.role_category = 'Data Analyst'
            GROUP BY js.skill
            ORDER BY count DESC
            LIMIT 10
        """,
        
        # Query 8: Remote vs Office Jobs
        "REMOTE VS OFFICE JOBS": """
            SELECT 
                CASE 
                    WHEN location = 'Remote' THEN 'Remote'
                    ELSE 'Office/Hybrid'
                END as work_type,
                COUNT(*) as job_count,
                ROUND(AVG(salary_avg), 1) as avg_salary
            FROM jobs
            WHERE salary_avg IS NOT NULL
            GROUP BY work_type
        """,
        
        # Query 9: Entry Level Opportunities
        "ENTRY LEVEL JOBS (0-1 YRS)": """
            SELECT 
                role_category,
                COUNT(*) as jobs_available,
                ROUND(AVG(salary_avg), 1) as avg_salary
            FROM jobs
            WHERE experience = '0-1 Yrs' AND salary_avg IS NOT NULL
            GROUP BY role_category
            ORDER BY jobs_available DESC
        """,
        
        # Query 10: Company Tier Analysis
        "SALARY BY COMPANY TIER": """
            SELECT 
                company_tier,
                COUNT(*) as job_count,
                ROUND(AVG(salary_avg), 1) as avg_salary,
                ROUND(MIN(salary_avg), 1) as min_salary,
                ROUND(MAX(salary_avg), 1) as max_salary
            FROM jobs
            WHERE salary_avg IS NOT NULL
            GROUP BY company_tier
            ORDER BY avg_salary DESC
        """,
        
        # Query 11: City + Role Combination
        "TOP CITY-ROLE COMBINATIONS": """
            SELECT 
                location,
                role_category,
                COUNT(*) as job_count
            FROM jobs
            GROUP BY location, role_category
            ORDER BY job_count DESC
            LIMIT 10
        """,
        
        # Query 12: Posting Recency
        "JOB POSTING FRESHNESS": """
            SELECT 
                posting_recency,
                COUNT(*) as job_count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM jobs), 1) as percentage
            FROM jobs
            GROUP BY posting_recency
            ORDER BY 
                CASE posting_recency
                    WHEN 'Very Recent' THEN 1
                    WHEN 'This Week' THEN 2
                    WHEN 'This Month' THEN 3
                    ELSE 4
                END
        """
    }
    
    # Execute queries and collect results
    output_lines = []
    output_lines.append("=" * 70)
    output_lines.append("INDIA JOB MARKET INTELLIGENCE 2025 - SQL ANALYSIS RESULTS")
    output_lines.append("=" * 70)
    output_lines.append(f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output_lines.append(f"Total Jobs Analyzed: 1200")
    output_lines.append("=" * 70 + "\n")
    
    for query_name, query in queries.items():
        print(f"\n📋 {query_name}")
        print("-" * 50)
        
        df_result = pd.read_sql_query(query, conn)
        print(df_result.to_string(index=False))
        
        # Add to output file
        output_lines.append(f"\n{'='*50}")
        output_lines.append(f"📊 {query_name}")
        output_lines.append("=" * 50)
        output_lines.append(df_result.to_string(index=False))
        output_lines.append("")
        
        results.append({
            'query_name': query_name,
            'result': df_result
        })
    
    conn.close()
    
    # Save results to file
    os.makedirs(os.path.dirname(QUERIES_OUTPUT), exist_ok=True)
    with open(QUERIES_OUTPUT, 'w') as f:
        f.write('\n'.join(output_lines))
    print(f"\n💾 Analysis results saved to: {QUERIES_OUTPUT}")
    
    return results


def export_for_tableau():
    """Export optimized datasets for Tableau"""
    print("\n" + "=" * 60)
    print("📊 EXPORTING DATA FOR TABLEAU")
    print("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    
    # Export 1: Main jobs data
    jobs_df = pd.read_sql_query("SELECT * FROM jobs", conn)
    jobs_df.to_csv(os.path.join(OUTPUT_DIR, "tableau_jobs.csv"), index=False)
    print("✓ Exported: tableau_jobs.csv")
    
    # Export 2: Skills frequency
    skills_freq = pd.read_sql_query("""
        SELECT skill, COUNT(*) as job_count
        FROM job_skills
        GROUP BY skill
        ORDER BY job_count DESC
    """, conn)
    skills_freq.to_csv(os.path.join(OUTPUT_DIR, "tableau_skills.csv"), index=False)
    print("✓ Exported: tableau_skills.csv")
    
    # Export 3: City-Role matrix
    city_role = pd.read_sql_query("""
        SELECT location, role_category, COUNT(*) as job_count,
               ROUND(AVG(salary_avg), 1) as avg_salary
        FROM jobs
        GROUP BY location, role_category
    """, conn)
    city_role.to_csv(os.path.join(OUTPUT_DIR, "tableau_city_role.csv"), index=False)
    print("✓ Exported: tableau_city_role.csv")
    
    # Export 4: Salary trends
    salary_trends = pd.read_sql_query("""
        SELECT experience_level, role_category,
               COUNT(*) as job_count,
               ROUND(AVG(salary_avg), 1) as avg_salary,
               ROUND(MIN(salary_avg), 1) as min_salary,
               ROUND(MAX(salary_avg), 1) as max_salary
        FROM jobs
        WHERE salary_avg IS NOT NULL
        GROUP BY experience_level, role_category
    """, conn)
    salary_trends.to_csv(os.path.join(OUTPUT_DIR, "tableau_salary_trends.csv"), index=False)
    print("✓ Exported: tableau_salary_trends.csv")
    
    conn.close()
    print("\n✅ All Tableau exports complete!")


if __name__ == "__main__":
    # Create database
    create_database()
    
    # Run analysis
    results = run_analysis_queries()
    
    # Export for Tableau
    export_for_tableau()
    
    print("\n" + "=" * 60)
    print("✅ PHASE 4 COMPLETE!")
    print("=" * 60)
