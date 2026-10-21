"""
India Job Market Intelligence 2025
Phase 3: Data Cleaning & Processing
Description: Cleans and processes raw job data for analysis
"""

import os
import pandas as pd
import numpy as np
import re
from collections import Counter

def load_data(filepath):
    """Load raw data"""
    print("📂 Loading raw data...")
    df = pd.read_csv(filepath)
    print(f"   Loaded {len(df)} records")
    return df


def extract_salary_range(salary_str):
    """Extract min and max salary from salary string"""
    if pd.isna(salary_str) or salary_str == "Not Disclosed":
        return None, None, None
    
    # Pattern: "X-Y Lacs PA" or "X.X-Y.Y Lacs PA"
    match = re.search(r'(\d+\.?\d*)-(\d+\.?\d*)', str(salary_str))
    if match:
        min_sal = float(match.group(1))
        max_sal = float(match.group(2))
        avg_sal = (min_sal + max_sal) / 2
        return min_sal, max_sal, avg_sal
    return None, None, None


def extract_experience_years(exp_str):
    """Extract numeric experience values"""
    if pd.isna(exp_str):
        return None, None
    
    exp_str = str(exp_str)
    
    # Handle "12+ Yrs"
    if "12+" in exp_str:
        return 12, 15
    
    # Pattern: "X-Y Yrs"
    match = re.search(r'(\d+)-(\d+)', exp_str)
    if match:
        return int(match.group(1)), int(match.group(2))
    
    return None, None


def parse_skills(skills_str):
    """Parse skills string into list"""
    if pd.isna(skills_str):
        return []
    return [s.strip() for s in str(skills_str).split(',')]


def clean_data(df):
    """Main cleaning function"""
    print("\n🧹 CLEANING DATA")
    print("-" * 40)
    
    # Create copy
    df_clean = df.copy()
    
    # 1. Extract salary components
    print("  ✓ Extracting salary ranges...")
    salary_data = df_clean['salary'].apply(lambda x: pd.Series(extract_salary_range(x)))
    df_clean['salary_min'] = salary_data[0]
    df_clean['salary_max'] = salary_data[1]
    df_clean['salary_avg'] = salary_data[2]
    df_clean['salary_disclosed'] = df_clean['salary'] != "Not Disclosed"
    
    # 2. Extract experience years
    print("  ✓ Parsing experience ranges...")
    exp_data = df_clean['experience'].apply(lambda x: pd.Series(extract_experience_years(x)))
    df_clean['exp_min'] = exp_data[0]
    df_clean['exp_max'] = exp_data[1]
    df_clean['exp_avg'] = (df_clean['exp_min'] + df_clean['exp_max']) / 2
    
    # 3. Create experience level categories
    print("  ✓ Creating experience levels...")
    def get_exp_level(exp_avg):
        if pd.isna(exp_avg):
            return "Unknown"
        if exp_avg <= 1:
            return "Entry Level"
        elif exp_avg <= 3:
            return "Junior"
        elif exp_avg <= 5:
            return "Mid-Level"
        elif exp_avg <= 8:
            return "Senior"
        else:
            return "Expert"
    
    df_clean['experience_level'] = df_clean['exp_avg'].apply(get_exp_level)
    
    # 4. Parse skills into lists and count
    print("  ✓ Processing skills...")
    df_clean['skills_list'] = df_clean['skills'].apply(parse_skills)
    df_clean['skills_count'] = df_clean['skills_list'].apply(len)
    
    # 5. Create salary brackets
    print("  ✓ Creating salary brackets...")
    def get_salary_bracket(salary_avg):
        if pd.isna(salary_avg):
            return "Not Disclosed"
        if salary_avg < 5:
            return "< 5 LPA"
        elif salary_avg < 10:
            return "5-10 LPA"
        elif salary_avg < 20:
            return "10-20 LPA"
        elif salary_avg < 35:
            return "20-35 LPA"
        else:
            return "35+ LPA"
    
    df_clean['salary_bracket'] = df_clean['salary_avg'].apply(get_salary_bracket)
    
    # 6. Clean location names
    print("  ✓ Standardizing locations...")
    location_map = {
        "Delhi NCR": "Delhi/NCR",
        "Bangalore": "Bengaluru",
    }
    df_clean['location_clean'] = df_clean['location'].replace(location_map)
    
    # 7. Create posting recency category
    print("  ✓ Categorizing posting dates...")
    def get_recency(posted):
        if "Today" in str(posted) or "1 Day" in str(posted):
            return "Very Recent"
        elif "Week" not in str(posted) and "Month" not in str(posted):
            return "This Week"
        elif "Week" in str(posted):
            return "This Month"
        else:
            return "Older"
    
    df_clean['posting_recency'] = df_clean['posted_date'].apply(get_recency)
    
    print(f"\n✅ Cleaning complete! {len(df_clean)} records processed")
    
    return df_clean


def analyze_skills(df):
    """Analyze skill frequencies"""
    print("\n📊 SKILL ANALYSIS")
    print("-" * 40)
    
    all_skills = []
    for skills_list in df['skills_list']:
        all_skills.extend(skills_list)
    
    skill_counts = Counter(all_skills)
    skill_df = pd.DataFrame(skill_counts.most_common(30), columns=['skill', 'count'])
    skill_df['percentage'] = (skill_df['count'] / len(df) * 100).round(1)
    
    print("\n🔝 TOP 15 MOST DEMANDED SKILLS:")
    for i, row in skill_df.head(15).iterrows():
        print(f"   {i+1}. {row['skill']}: {row['count']} jobs ({row['percentage']}%)")
    
    return skill_df


def create_skills_matrix(df):
    """Create skill-by-role matrix"""
    print("\n📋 Creating skills matrix by role...")
    
    skill_by_role = {}
    for role in df['role_category'].unique():
        role_df = df[df['role_category'] == role]
        all_skills = []
        for skills_list in role_df['skills_list']:
            all_skills.extend(skills_list)
        skill_counts = Counter(all_skills)
        skill_by_role[role] = dict(skill_counts.most_common(10))
    
    return skill_by_role


def generate_summary_stats(df):
    """Generate summary statistics"""
    print("\n📈 SUMMARY STATISTICS")
    print("=" * 50)
    
    stats = {
        "total_jobs": len(df),
        "unique_companies": df['company'].nunique(),
        "unique_titles": df['title'].nunique(),
        "avg_salary_disclosed": df[df['salary_disclosed']]['salary_avg'].mean(),
        "median_salary": df[df['salary_disclosed']]['salary_avg'].median(),
        "avg_skills_required": df['skills_count'].mean(),
        "most_common_location": df['location'].mode()[0],
        "most_common_role": df['role_category'].mode()[0],
    }
    
    print(f"  Total Jobs: {stats['total_jobs']}")
    print(f"  Unique Companies: {stats['unique_companies']}")
    print(f"  Unique Titles: {stats['unique_titles']}")
    print(f"  Avg Salary (when disclosed): {stats['avg_salary_disclosed']:.1f} LPA")
    print(f"  Median Salary: {stats['median_salary']:.1f} LPA")
    print(f"  Avg Skills Required: {stats['avg_skills_required']:.1f}")
    print(f"  Most Jobs Location: {stats['most_common_location']}")
    print(f"  Most Jobs Role: {stats['most_common_role']}")
    
    return stats


if __name__ == "__main__":
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(root_dir, "data")
    
    # Load raw data
    raw_file = os.path.join(data_dir, "india_jobs_raw.csv")
    df = load_data(raw_file)
    
    # Clean data
    df_clean = clean_data(df)
    
    # Analyze skills
    skills_df = analyze_skills(df_clean)
    
    # Generate summary
    stats = generate_summary_stats(df_clean)
    
    # Save cleaned data
    clean_file = os.path.join(data_dir, "india_jobs_cleaned.csv")
    df_clean.to_csv(clean_file, index=False, encoding='utf-8')
    print(f"\n💾 Saved cleaned data to: {clean_file}")
    
    # Save skills analysis
    skills_file = os.path.join(data_dir, "skills_analysis.csv")
    skills_df.to_csv(skills_file, index=False, encoding='utf-8')
    print(f"💾 Saved skills analysis to: {skills_file}")
    
    # Display new columns
    print("\n📋 New Columns Added:")
    new_cols = ['salary_min', 'salary_max', 'salary_avg', 'salary_disclosed', 
                'exp_min', 'exp_max', 'exp_avg', 'experience_level',
                'skills_count', 'salary_bracket', 'location_clean', 'posting_recency']
    for col in new_cols:
        print(f"   - {col}")
    
    print("\n✅ PHASE 3 COMPLETE!")
