import pandas as pd

def recommend_courses(user_skills, course_data_path="data/courses.csv"):
    df = pd.read_csv(course_data_path)

    # Sanity check: Make sure necessary columns exist
    required_columns = ['skills_taught', 'rating']
    for col in required_columns:
        if col not in df.columns:
            raise KeyError(f"Column '{col}' not found in the dataset!")

    recommendations = []

    for _, row in df.iterrows():
        skills_str = row.get('skills_taught')

        # Skip rows with missing or invalid skills
        if pd.isna(skills_str) or not isinstance(skills_str, str):
            continue

        course_skills = [skill.strip().lower() for skill in skills_str.split(',') if skill.strip()]

        # Check if any user skill matches course skills
        if any(skill.lower() in course_skills for skill in user_skills):
            recommendations.append(row)

    # Convert matched rows to DataFrame
    rec_df = pd.DataFrame(recommendations)

    # If no matching courses, return top-rated overall
    if rec_df.empty:
        return df.sort_values(by='rating', ascending=False).head(10)

    return rec_df.sort_values(by='rating', ascending=False).head(10)
