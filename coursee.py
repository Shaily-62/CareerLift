from datasets import load_dataset
import pandas as pd

# Load dataset from HuggingFace
ds = load_dataset("azrai99/coursera-course-dataset")

# Convert to pandas DataFrame and select top 600 records
df = ds["train"].to_pandas().head(600)

# Safely convert 'rating' to float, replacing non-numeric with 0
df["rating"] = pd.to_numeric(df["rating"], errors='coerce').fillna(0)

# Safely convert 'Level' to string and fill missing values
df["Level"] = df["Level"].astype(str).fillna("Beginner")

# Safely extract skills, even if null or not a list
def extract_skills(skill_data):
    if isinstance(skill_data, list):
        return ", ".join(skill_data)
    elif isinstance(skill_data, str):
        return skill_data
    else:
        return ""

# Build the cleaned output DataFrame
df_out = pd.DataFrame({
    "course_name": df["title"].astype(str),
    "platform": df["Organization"].fillna("Coursera").astype(str),
    "skills_taught": df["Skills"].apply(extract_skills),
    "course_url": df["URL"].astype(str),
    "difficulty": df["Level"],
    "rating": df["rating"]
})

# Save to CSV
df_out.to_csv("newcourses.csv", index=False)
print("✅ Saved cleaned 600+ courses to newcourses.csv")
