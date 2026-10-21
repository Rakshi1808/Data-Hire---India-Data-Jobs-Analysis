"""Export cleaned dataset to data/dashboard_data.js so output/dashboard.html
can read the real data (works when the HTML is opened by double-click)."""
import json, os
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
df = pd.read_csv(os.path.join(ROOT, "data", "india_jobs_cleaned.csv"))
cols = ["job_id", "company", "company_tier", "location_clean", "role_category",
        "experience_level", "salary_avg", "salary_bracket", "skills", "collected_date"]
out = df[cols].astype(object).where(df[cols].notna(), None)
payload = {"columns": cols, "rows": out.values.tolist()}
path = os.path.join(ROOT, "data", "dashboard_data.js")
with open(path, "w", encoding="utf-8") as f:
    f.write("window.JOBS_DATA = " + json.dumps(payload, ensure_ascii=False) + ";\n")
print(f"Wrote {len(df)} rows -> {path}")
